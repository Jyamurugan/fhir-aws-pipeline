import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { SqsEventSource } from 'aws-cdk-lib/aws-lambda-event-sources';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sns_subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';

export class FhirAwsPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, {
      ...props,
      env: {
        region: 'us-east-2',
      },
    });
    const accountId = cdk.Stack.of(this).account;
    /**
     * S3 Bucket: fhir-bundle-source
     * S3 Bucket: fhir-resources
     *  subpaths patient, claims, visits, diagnosis, procedures, medications
     * 
     * S3 Queue: fhir-bundle-queue
     * S3 Queue: fhir-bundle-queue-dlq
     * 
     * S3 Queue: fhir-patient-queue
     * S3 Queue: fhir-patient-queue-dlq
     * 
     * S3 Queue: fhir-claims-queue
     * S3 Queue: fhir-claims-queue-dlq
     * 
     * S3 Queue: fhir-visits-queue
     * S3 Queue: fhir-visits-queue-dlq
     * 
     * S3 Queue: fhir-diagnosis-queue
     * S3 Queue: fhir-diagnosis-queue-dlq
     * 
     * S3 Queue: fhir-procedures-queue
     * S3 Queue: fhir-procedures-queue-dlq
     * 
     * S3 Queue: fhir-medications-queue
     * S3 Queue: fhir-medications-queue-dlq
     * 
     * 
     * Function: fhir-bundle-processor
     * Function: fhir-patient-processor
     * Function: fhir-claims-processor
     * Function: fhir-visits-processor
     * Function: fhir-diagnosis-processor
     * Function: fhir-procedures-processor
     * Function: fhir-medications-processor
     * 
     * Workflow (FHIR Bundle to FHIR Resources):
     * 1. S3 Bucket: fhir-bundle-source
     * 2. Destination S3 Queue: fhir-bundle-queue
     * 4. Function: fhir-bundle-processor
     * 5. Destination fhir-*resource-queue  (patient, claims, visits, diagnosis, procedures, medications)
     * 6. Function: fhir-*resource-processor
     * 7. Destination S3 Bucket: fhir-resources
     * 
     * 
     *  Workflow 2 - Resources
     * 
     *  API Gateway: fhir-api
     * Lambda Function: fhir-bundle-to-s3
     * 
     * Workflow (API Gateway to S3):
     *  API Gateway: fhir-api
     *  authentication using api-key
     *  max of 100 requests per second
     *  throttling of 20 requests per second
     *  maximum payload size of 10 MB
     *  request/response in JSON format
     *  URL POST /fhir/budle
     *  invokes the lambda function fhir-bundle-to-s3
     *  destination bucket fhir-bundle-source
     */

    // code goes here
    // S3 Buckets
    const fhirBundleSourceBucket = new s3.Bucket(this, 'fhir-bundle-source');
    const fhirResourcesBucket = new s3.Bucket(this, 'fhir-resources');
    const sourcecodebucket = s3.Bucket.fromBucketName(this, 'sourcecodebucket', `${accountId}-fhir-pipeline-source`);

    // SQS Queues and Dead Letter Queues
    const createQueueWithDLQ = (queueName: string) => {
      const dlq = new sqs.Queue(this, `${queueName}-dlq`);
      const queue = new sqs.Queue(this, queueName, {
        deadLetterQueue: {
          queue: dlq,
          maxReceiveCount: 5,
        },
      });
      return { queue, dlq };
    };

    const fhirBundleQueue = createQueueWithDLQ('fhir-bundle-queue');
    const fhirPatientQueue = createQueueWithDLQ('fhir-patient-queue');
    const fhirClaimsQueue = createQueueWithDLQ('fhir-claims-queue');
    // const fhirVisitsQueue = createQueueWithDLQ('fhir-visits-queue');
    // const fhirDiagnosisQueue = createQueueWithDLQ('fhir-diagnosis-queue');
    // const fhirProceduresQueue = createQueueWithDLQ('fhir-procedures-queue');
    // const fhirMedicationsQueue = createQueueWithDLQ('fhir-medications-queue');

    // SNS Topic
    const fhirBundleTopic = new sns.Topic(this, 'fhir-bundle-topic');

    // Subscribe SQS queues to the SNS topic
    fhirBundleTopic.addSubscription(new sns_subscriptions.SqsSubscription(fhirPatientQueue.queue,
      {
        filterPolicy: {
          resourceType: sns.SubscriptionFilter.stringFilter({
            allowlist: ['Patient'],
          }),
        }
      }
    ));
    fhirBundleTopic.addSubscription(new sns_subscriptions.SqsSubscription(fhirClaimsQueue.queue));
    // fhirBundleTopic.addSubscription(new sns_subscriptions.SqsSubscription(fhirVisitsQueue.queue));
    // fhirBundleTopic.addSubscription(new sns_subscriptions.SqsSubscription(fhirDiagnosisQueue.queue));
    // fhirBundleTopic.addSubscription(new sns_subscriptions.SqsSubscription(fhirProceduresQueue.queue));
    // fhirBundleTopic.addSubscription(new sns_subscriptions.SqsSubscription(fhirMedicationsQueue.queue));

    // Lambda Functions
    const createLambdaFunction = (functionName: string, environment?: { [key: string]: string }) => {
      return new lambda.Function(this, functionName, {
        runtime: lambda.Runtime.PYTHON_3_13,
        handler: 'main.handler',
        code: lambda.Code.fromBucket(sourcecodebucket, `projects/${functionName}/package.zip`),
        environment,
        functionName,
        timeout: cdk.Duration.seconds(60),
        memorySize: 512,
      });
    };

    const fhirBundleProcessor = createLambdaFunction('fhir-bundle-processor', {
      DESTINATION_TOPIC_ARN: fhirBundleTopic.topicArn
    });
    fhirBundleSourceBucket.grantRead(fhirBundleProcessor);
    const fhirPatientProcessor = createLambdaFunction('fhir-patient-processor', { DESTINATION_BUCKET: fhirResourcesBucket.bucketName });
    const fhirClaimsProcessor = createLambdaFunction('fhir-claims-processor', { DESTINATION_BUCKET: fhirResourcesBucket.bucketName });
    // const fhirVisitsProcessor = createLambdaFunction('fhir-visits-processor', { DESTINATION_BUCKET: fhirResourcesBucket.bucketName });
    // const fhirDiagnosisProcessor = createLambdaFunction('fhir-diagnosis-processor', { DESTINATION_BUCKET: fhirResourcesBucket.bucketName });
    // const fhirProceduresProcessor = createLambdaFunction('fhir-procedures-processor', { DESTINATION_BUCKET: fhirResourcesBucket.bucketName });
    // const fhirMedicationsProcessor = createLambdaFunction('fhir-medications-processor', { DESTINATION_BUCKET: fhirResourcesBucket.bucketName });

    // Grant write permissions to the Lambda functions
    fhirResourcesBucket.grantWrite(fhirBundleProcessor);
    fhirResourcesBucket.grantWrite(fhirPatientProcessor);
    fhirResourcesBucket.grantWrite(fhirClaimsProcessor);
    // fhirResourcesBucket.grantWrite(fhirVisitsProcessor);
    // fhirResourcesBucket.grantWrite(fhirDiagnosisProcessor);
    // fhirResourcesBucket.grantWrite(fhirProceduresProcessor);
    // fhirResourcesBucket.grantWrite(fhirMedicationsProcessor);

    // Grant publish permissions to the Lambda function
    fhirBundleTopic.grantPublish(fhirBundleProcessor);

    // S3 Bucket Notifications
    fhirBundleSourceBucket.addEventNotification(s3.EventType.OBJECT_CREATED, new s3n.SqsDestination(fhirBundleQueue.queue));

    // Lambda Event Sources
    const createBatchEventSource = (queue: sqs.Queue) => {
      return new SqsEventSource(queue, {
        batchSize: 10,
        maxBatchingWindow: cdk.Duration.seconds(60),
        reportBatchItemFailures: true,
      });
    };

    fhirBundleProcessor.addEventSource(createBatchEventSource(fhirBundleQueue.queue));
    fhirPatientProcessor.addEventSource(createBatchEventSource(fhirPatientQueue.queue));
    fhirClaimsProcessor.addEventSource(createBatchEventSource(fhirClaimsQueue.queue));
    // fhirVisitsProcessor.addEventSource(createBatchEventSource(fhirVisitsQueue.queue));
    // fhirDiagnosisProcessor.addEventSource(createBatchEventSource(fhirDiagnosisQueue.queue));
    // fhirProceduresProcessor.addEventSource(createBatchEventSource(fhirProceduresQueue.queue));
    // fhirMedicationsProcessor.addEventSource(createBatchEventSource(fhirMedicationsQueue.queue));

    // Workflow 2 - API Gateway and Lambda Function
    const fhirBundleToS3 = new lambda.Function(this, 'fhir-bundle-to-s3', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
      def handler(event, context):
        print(event)
        return {
          'statusCode': 200,
          'body': 'Event received'
        }
      `),
      environment: {
        DESTINATION_BUCKET: fhirBundleSourceBucket.bucketName,
        name: 'fhir-bundle-to-s3',
      },
    });

    fhirBundleSourceBucket.grantWrite(fhirBundleToS3);

    const api = new apigateway.RestApi(this, 'fhir-api', {
      restApiName: 'FHIR Service',
      description: 'This service handles FHIR bundles.',
      deployOptions: {
        stageName: 'prod',
        throttlingRateLimit: 20,
        throttlingBurstLimit: 100,
      },
    });

    const plan = api.addUsagePlan('UsagePlan', {
      name: 'Easy',
      throttle: {
        rateLimit: 100,
        burstLimit: 20,
      },
    });

    plan.addApiStage({
      stage: api.deploymentStage,
    });

    const fhir = api.root.addResource('fhir');
    const bundle = fhir.addResource('bundle');
    const postIntegration = new apigateway.LambdaIntegration(fhirBundleToS3);

    bundle.addMethod('POST', postIntegration, {
      apiKeyRequired: true,
      requestModels: {
        'application/json': new apigateway.Model(this, 'RequestModel', {
          restApi: api,
          contentType: 'application/json',
          schema: { schema: apigateway.JsonSchemaVersion.DRAFT4, title: 'FHIRBundle', type: apigateway.JsonSchemaType.OBJECT },
        }),
      },
    });
  }
}

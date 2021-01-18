create:
	aws cloudformation create-stack --stack-name main-stack --template-body file://main-cloudformation.yaml --parameters file://parameters.json --region eu-central-1  --capabilities CAPABILITY_NAMED_IAM

update:
	aws cloudformation update-stack --stack-name main-stack --template-body file://main-cloudformation.yaml --parameters file://parameters.json --region eu-central-1  --capabilities CAPABILITY_NAMED_IAM

delete:
	aws cloudformation delete-stack --stack-name main-stack

describe:
	aws cloudformation describe-stacks --stack-name main-stack --region eu-central-1 > stack.json

testuser:
	aws cognito-idp sign-up --client-id 39ien2pcmu4j9t0ept17e9ja6e --region eu-central-1 --username test --password testpw --user-attributes Name="email",Value="test@test.de"
	aws cognito-idp admin-confirm-sign-up --region eu-central-1 --user-pool-id eu-central-1_mpDnI1bfq --username test
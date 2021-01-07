create:
	aws cloudformation create-stack --stack-name main-stack --template-body file://main-cloudformation.yaml --parameters file://parameters.json --region eu-central-1  --capabilities CAPABILITY_NAMED_IAM

update:
	aws cloudformation update-stack --stack-name main-stack --template-body file://main-cloudformation.yaml --parameters file://parameters.json --region eu-central-1  --capabilities CAPABILITY_NAMED_IAM

delete:
	aws cloudformation delete-stack --stack-name main-stack
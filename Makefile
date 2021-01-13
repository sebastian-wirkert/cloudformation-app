create:
	aws cloudformation create-stack --stack-name main-stack --template-body file://main-cloudformation.yaml --parameters file://parameters.json --region eu-central-1  --capabilities CAPABILITY_NAMED_IAM

update:
	aws cloudformation update-stack --stack-name main-stack --template-body file://main-cloudformation.yaml --parameters file://parameters.json --region eu-central-1  --capabilities CAPABILITY_NAMED_IAM

delete:
	aws cloudformation delete-stack --stack-name main-stack

testuser:
	aws cognito-idp sign-up --client-id 3kot71pldcmf2h3r1rfsc14iv8 --region eu-central-1 --username sebastian.wirkert@posteo.de --password Bitchibitch --user-attributes Name="email",Value="sebastian.wirkert@posteo.de"
	aws cognito-idp admin-confirm-sign-up --region eu-central-1 --user-pool-id eu-central-1_mpDnI1bfq --username sebastian.wirkert@posteo.de
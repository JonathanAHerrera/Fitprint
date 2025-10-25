# Fitprint Deployment Guide (AWS)

This guide walks through deploying the Fitprint Expo web client and FastAPI backend on AWS using hackathon credits. The stack uses DynamoDB for persistence and optional S3/Gemini integrations.

## 1. Prerequisites

- AWS account with credits and programmatic access (IAM user with AdministratorAccess during setup).
- AWS CLI v2 installed locally and configured (`aws configure`).
- Docker installed locally for building the backend image.
- Node.js 18+ and npm for frontend builds.
- Google OAuth web client ID already configured (matches the Expo app extras).
- DynamoDB table to store user profiles (primary key `user_id`).

```bash
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## 2. Backend (FastAPI) on AWS App Runner

### 2.1 Build and push the image

```bash
# From repository root
export AWS_REGION=us-west-2 # choose the region you will deploy into
export ECR_REPO=fitprint-api

aws ecr create-repository --repository-name "$ECR_REPO" --region "$AWS_REGION"

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.$AWS_REGION.amazonaws.com

docker build -t $ECR_REPO -f fitprint_server/Dockerfile .

docker tag $ECR_REPO:latest $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

docker push $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
```

### 2.2 Provision App Runner

1. In the AWS console go to **App Runner** → **Create service**.
2. Choose **Container registry** → **ECR** → select the `fitprint-api` image.
3. Configure service:
   - Service name: `fitprint-api`.
   - CPU/Memory: 1 vCPU / 2 GB is sufficient; scale up if needed.
   - Port: `8000`.
4. Set environment variables (use **Encrypted** for secrets):

| Variable | Purpose |
| -------- | ------- |
| `AWS_REGION` | Region for DynamoDB and S3 |
| `USERS_TABLE_NAME` | DynamoDB table name, e.g. `fitprint-users` |
| `DYNAMODB_TABLE_NAME` | If other services require it |
| `S3_BUCKET_NAME` | Bucket for uploads (optional) |
| `GEMINI_API_KEY` | Gemini API key (optional) |
| `GOOGLE_API_KEY` | For search service (optional) |
| `GOOGLE_SEARCH_ENGINE_ID` | Custom search engine ID |
| `GOOGLE_CLIENT_ID` | The Google OAuth web client ID |

5. Assign an IAM role (new or existing) that grants:
   - `AmazonDynamoDBFullAccess` (or a scoped policy to the table).
   - Optional: `AmazonS3FullAccess` to the bucket. Replace with least privilege later.
6. Create the service and note the HTTPS URL (e.g. `https://fitprint-api.us-east-1.awsapprunner.com`).

### 2.3 CORS

In production tighten the `allow_origins` list in `fitprint_server/main.py` to the Amplify domain(s) before redeploying.

## 3. Frontend (Expo Web) on AWS Amplify Hosting

### 3.1 Prepare environment variables

In Amplify console you will set the following build-time variables:

| Variable | Value |
| -------- | ----- |
| `EXPO_PUBLIC_BACKEND_BASE_URL` | App Runner URL (e.g. `https://5jeggs9izc.us-west-2.awsapprunner.com`) |
| `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID` | Same as backend `GOOGLE_CLIENT_ID` |
| `EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID` | Android client ID |
| `EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID` | iOS client ID |
| `EXPO_PUBLIC_EXPO_AUTH_REDIRECT` | Production redirect (for web use App Runner domain or custom domain) |

### 3.2 Connect Amplify

1. Push the repo to GitHub.
2. In Amplify console: **New app** → **Host web app** → select repository/branch.
3. Amplify detects `amplify.yml` (see below) and runs the build.
4. After initial deploy, Amplify provides a default domain like `https://main.<id>.amplifyapp.com`.

### 3.3 Build spec (`amplify.yml`)

Amplify uses the included `amplify.yml` to build and export the static site. If you need to customize, edit the file in the repo.

## 4. Optional: Custom Domain

- Use Route 53 or your DNS provider to point a subdomain to Amplify. Add the domain in Amplify and follow the automatic ACM validation steps.
- For the backend, create an AWS Certificate Manager certificate and map it via CloudFront or an Application Load Balancer in front of App Runner if you need a custom hostname. Otherwise use the default App Runner URL.

## 5. Post-Deployment Checklist

- Confirm `/health` endpoint responds from the App Runner URL.
- Confirm Google sign-in works in Amplify-hosted frontend; adjust OAuth Authorized JavaScript Origins to include the Amplify domain.
- Enable CloudWatch alarms for App Runner error rates and latency.
- Configure AWS Budgets to track credit consumption.
- Rotate any plaintext secrets into AWS Secrets Manager and reference them in App Runner.

## 6. Local Verification Commands

```bash
# Backend unit/integration tests (if any)
cd fitprint_server
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend web preview
cd ../fitprint
npm install
npx expo export --platform web --output-dir dist
npx serve dist
```

## 7. Troubleshooting

- **401 errors after sign-in**: make sure App Runner `GOOGLE_CLIENT_ID` matches the Expo web client ID.
- **DynamoDB access denied**: update the App Runner service role with a policy granting `dynamodb:*` on the table ARN.
- **Amplify build fails**: ensure Node 18+ runtime is selected in the Amplify build image or add `NODE_VERSION` variable.
- **CORS failures**: update `allow_origins` in FastAPI or use `allow_origin_regex` for Amplify wildcard domains.

With these steps in place you can deploy both frontend and backend using AWS hackathon credits. Update the guide as infrastructure evolves.

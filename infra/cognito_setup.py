#!/usr/bin/env python3
"""
Cognito Setup Script
Creates Cognito User Pool, App Client, and Domain for OAuth2 authentication
"""

import boto3
import json
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class CognitoSetup:
    """Setup Amazon Cognito for AgentCore authentication"""

    def __init__(self, region: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.cognito = boto3.client("cognito-idp", region_name=self.region)
        self.account_id = boto3.client("sts").get_caller_identity()["Account"]

    def create_user_pool(self, pool_name: str = "travel-agent-pool") -> Dict[str, Any]:
        """Create Cognito User Pool"""
        print(f"Creating Cognito User Pool: {pool_name}")

        try:
            response = self.cognito.create_user_pool(
                PoolName=pool_name,
                Policies={
                    "PasswordPolicy": {
                        "MinimumLength": 12,
                        "RequireUppercase": True,
                        "RequireLowercase": True,
                        "RequireNumbers": True,
                        "RequireSymbols": True,
                        "TemporaryPasswordValidityDays": 7
                    }
                },
                AutoVerifiedAttributes=["email"],
                UsernameAttributes=["email"],
                UsernameConfiguration={"CaseSensitive": False},
                MfaConfiguration="OPTIONAL",
                EmailConfiguration={
                    "EmailSendingAccount": "COGNITO_DEFAULT"
                },
                UserAttributeUpdateSettings={
                    "AttributesRequireVerificationBeforeUpdate": ["email"]
                },
                AccountRecoverySetting={
                    "RecoveryMechanisms": [
                        {"Priority": 1, "Name": "verified_email"}
                    ]
                },
                Tags={
                    "Application": "TravelAgent",
                    "Environment": os.getenv("ENVIRONMENT", "development"),
                    "ManagedBy": "boto3"
                }
            )

            user_pool_id = response["UserPool"]["Id"]
            print(f"✓ User Pool created: {user_pool_id}")

            return {
                "user_pool_id": user_pool_id,
                "arn": response["UserPool"]["Arn"]
            }

        except self.cognito.exceptions.UserPoolAddOnNotEnabledException as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error creating user pool: {e}")
            sys.exit(1)

    def create_app_client(
        self,
        user_pool_id: str,
        client_name: str = "travel-agent-client"
    ) -> Dict[str, Any]:
        """Create Cognito App Client"""
        print(f"Creating App Client: {client_name}")

        callback_url = os.getenv("OAUTH_CALLBACK_URL", "http://localhost:8080/callback")

        try:
            response = self.cognito.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName=client_name,
                GenerateSecret=True,  # Required for server-side OAuth
                RefreshTokenValidity=30,  # 30 days
                AccessTokenValidity=60,  # 60 minutes
                IdTokenValidity=60,  # 60 minutes
                TokenValidityUnits={
                    "AccessToken": "minutes",
                    "IdToken": "minutes",
                    "RefreshToken": "days"
                },
                ReadAttributes=["email", "name", "email_verified"],
                WriteAttributes=["email", "name"],
                ExplicitAuthFlows=[
                    "ALLOW_USER_PASSWORD_AUTH",
                    "ALLOW_REFRESH_TOKEN_AUTH",
                    "ALLOW_USER_SRP_AUTH"
                ],
                SupportedIdentityProviders=["COGNITO"],
                CallbackURLs=[callback_url],
                LogoutURLs=[callback_url],
                AllowedOAuthFlows=["code", "implicit"],
                AllowedOAuthScopes=["openid", "profile", "email"],
                AllowedOAuthFlowsUserPoolClient=True,
                PreventUserExistenceErrors="ENABLED"
            )

            client_id = response["UserPoolClient"]["ClientId"]
            client_secret = response["UserPoolClient"]["ClientSecret"]

            print(f"✓ App Client created: {client_id}")
            print(f"  Client Secret: {client_secret[:10]}... (stored securely)")

            return {
                "client_id": client_id,
                "client_secret": client_secret
            }

        except Exception as e:
            print(f"✗ Error creating app client: {e}")
            sys.exit(1)

    def create_domain(
        self,
        user_pool_id: str,
        domain_prefix: str = None
    ) -> Dict[str, Any]:
        """Create Cognito Domain"""
        if not domain_prefix:
            domain_prefix = f"travel-agent-{self.account_id[:8]}"

        print(f"Creating Cognito Domain: {domain_prefix}")

        try:
            response = self.cognito.create_user_pool_domain(
                Domain=domain_prefix,
                UserPoolId=user_pool_id
            )

            domain_url = f"https://{domain_prefix}.auth.{self.region}.amazoncognito.com"

            print(f"✓ Domain created: {domain_url}")

            return {
                "domain": domain_prefix,
                "domain_url": domain_url
            }

        except self.cognito.exceptions.InvalidParameterException as e:
            if "Domain already exists" in str(e):
                print(f"✓ Domain already exists: {domain_prefix}")
                return {
                    "domain": domain_prefix,
                    "domain_url": f"https://{domain_prefix}.auth.{self.region}.amazoncognito.com"
                }
            else:
                print(f"✗ Error creating domain: {e}")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Error creating domain: {e}")
            sys.exit(1)

    def create_test_user(
        self,
        user_pool_id: str,
        email: str,
        temporary_password: str
    ) -> Dict[str, Any]:
        """Create a test user"""
        print(f"Creating test user: {email}")

        try:
            response = self.cognito.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"},
                    {"Name": "name", "Value": "Test User"}
                ],
                TemporaryPassword=temporary_password,
                MessageAction="SUPPRESS"  # Don't send email
            )

            print(f"✓ Test user created: {email}")
            print(f"  Temporary password: {temporary_password}")
            print(f"  User must change password on first login")

            return {
                "username": response["User"]["Username"],
                "status": response["User"]["UserStatus"]
            }

        except self.cognito.exceptions.UsernameExistsException:
            print(f"✓ User already exists: {email}")
            return {"username": email, "status": "EXISTS"}
        except Exception as e:
            print(f"✗ Error creating test user: {e}")
            sys.exit(1)

    def save_config(self, config: Dict[str, Any], output_file: str = "config/.env"):
        """Save configuration to .env file"""
        print(f"\nSaving configuration to {output_file}")

        try:
            # Read existing .env
            env_path = os.path.join(os.path.dirname(__file__), "..", output_file)
            existing_config = {}

            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            existing_config[key] = value

            # Update with new values
            existing_config.update({
                "COGNITO_USER_POOL_ID": config["user_pool_id"],
                "COGNITO_APP_CLIENT_ID": config["client_id"],
                "COGNITO_DOMAIN": config["domain"]
            })

            # Write back
            with open(env_path, "w") as f:
                f.write("# Elastic Configuration\n")
                f.write(f"ES_URL={existing_config.get('ES_URL', '')}\n")
                f.write(f"ES_API_KEY={existing_config.get('ES_API_KEY', '')}\n\n")

                f.write("# AWS Configuration\n")
                f.write(f"AWS_REGION={existing_config.get('AWS_REGION', self.region)}\n\n")

                f.write("# AgentCore Runtime Configuration\n")
                f.write(f"AGENTCORE_RUNTIME_ID={existing_config.get('AGENTCORE_RUNTIME_ID', '')}\n")
                f.write(f"AGENTCORE_GATEWAY_URL={existing_config.get('AGENTCORE_GATEWAY_URL', '')}\n")
                f.write(f"AGENTCORE_MEMORY_NAMESPACE={existing_config.get('AGENTCORE_MEMORY_NAMESPACE', '')}\n\n")

                f.write("# Cognito Configuration\n")
                f.write(f"COGNITO_USER_POOL_ID={config['user_pool_id']}\n")
                f.write(f"COGNITO_APP_CLIENT_ID={config['client_id']}\n")
                f.write(f"COGNITO_DOMAIN={config['domain']}\n\n")

                f.write("# MCP Server Configuration\n")
                f.write(f"MCP_SERVER_PORT={existing_config.get('MCP_SERVER_PORT', '8000')}\n")
                f.write(f"MCP_SERVER_HOST={existing_config.get('MCP_SERVER_HOST', '0.0.0.0')}\n\n")

                f.write("# Application Configuration\n")
                f.write(f"LOG_LEVEL={existing_config.get('LOG_LEVEL', 'INFO')}\n")
                f.write(f"ENVIRONMENT={existing_config.get('ENVIRONMENT', 'development')}\n\n")

                f.write("# Session Configuration\n")
                f.write(f"SESSION_TIMEOUT_SECONDS={existing_config.get('SESSION_TIMEOUT_SECONDS', '3600')}\n")
                f.write(f"MAX_CONVERSATION_TURNS={existing_config.get('MAX_CONVERSATION_TURNS', '50')}\n\n")

                f.write("# Security\n")
                f.write(f"ENABLE_ENCRYPTION={existing_config.get('ENABLE_ENCRYPTION', 'true')}\n")

            print(f"✓ Configuration saved to {env_path}")

        except Exception as e:
            print(f"✗ Error saving configuration: {e}")
            sys.exit(1)

    def setup_all(self) -> Dict[str, Any]:
        """Run complete Cognito setup"""
        print("="*60)
        print("Amazon Cognito Setup for Travel Agent")
        print("="*60)
        print()

        # Create User Pool
        pool_info = self.create_user_pool()

        # Create App Client
        client_info = self.create_app_client(pool_info["user_pool_id"])

        # Create Domain
        domain_info = self.create_domain(pool_info["user_pool_id"])

        # Create test user
        test_user = self.create_test_user(
            pool_info["user_pool_id"],
            email="test@example.com",
            temporary_password="TempPass123!"
        )

        # Combine all info
        config = {
            **pool_info,
            **client_info,
            **domain_info,
            "test_user": test_user
        }

        # Save to .env
        self.save_config(config)

        print()
        print("="*60)
        print("Cognito Setup Complete!")
        print("="*60)
        print()
        print(f"User Pool ID: {config['user_pool_id']}")
        print(f"App Client ID: {config['client_id']}")
        print(f"Domain: {config['domain_url']}")
        print()
        print("OAuth2 URLs:")
        print(f"  Authorize: {config['domain_url']}/oauth2/authorize")
        print(f"  Token: {config['domain_url']}/oauth2/token")
        print(f"  UserInfo: {config['domain_url']}/oauth2/userInfo")
        print()
        print("Test User:")
        print(f"  Email: test@example.com")
        print(f"  Temporary Password: TempPass123!")
        print(f"  (Must change on first login)")
        print()

        return config


def main():
    """Main entry point"""
    setup = CognitoSetup()
    config = setup.setup_all()

    # Print summary
    print("Next steps:")
    print("1. Update config/.env with the values above")
    print("2. Run: python infra/agentcore_deploy.py")
    print("3. Start MCP server: python mcp/elastic_mcp_server.py")
    print("4. Run agents: python main.py")
    print()


if __name__ == "__main__":
    main()

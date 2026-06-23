#!/usr/bin/env python3
"""
Customer Support Agent - Main Entry Point
Interactive REPL for testing the hybrid agent
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.simple_customer_support import SimpleCustomerSupportAgent

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("   CUSTOMER SUPPORT AGENT - Hybrid Architecture")
    print("   Elastic AgenticBuilder + Strands Agents SDK")
    print("="*70)
    print("\nType your question or command:")
    print("  - Ask about products, orders, policies")
    print("  - Type 'help' for available commands")
    print("  - Type 'quit' or 'exit' to end session")
    print("  - Type 'analytics' to see agent statistics")
    print("="*70 + "\n")


def print_help():
    """Print help message"""
    print("\n" + "-"*70)
    print("AVAILABLE COMMANDS:")
    print("-"*70)
    print("  help                - Show this help message")
    print("  quit / exit         - End the session")
    print("  analytics           - Show agent analytics and statistics")
    print("  clear               - Clear conversation history")
    print("  status              - Show session information")
    print("\nEXAMPLE QUERIES:")
    print("  - What is your return policy?")
    print("  - Check status of order ORD-12345")
    print("  - Show me wireless headphones under $100")
    print("  - Is product PROD-001 in stock?")
    print("  - I need help with a defective product")
    print("-"*70 + "\n")


def print_analytics(agent):
    """Print agent analytics"""
    print("\n" + "="*70)
    print("AGENT ANALYTICS")
    print("="*70)

    analytics = agent.get_analytics()

    print(f"\nSession ID: {analytics.get('session_id', 'N/A')}")
    print("\nTool Usage Statistics:")
    print("-"*70)

    tool_stats = analytics.get("tool_statistics", [])
    if tool_stats:
        for tool in tool_stats:
            print(f"  {tool['name']}")
            print(f"    Usage Count:   {tool['usage_count']}")
            print(f"    Success Rate:  {tool['success_rate']:.2%}")
            print(f"    Avg Latency:   {tool['avg_latency_ms']:.2f}ms")
            print()
    else:
        print("  No tool usage data yet")

    print("="*70 + "\n")


def print_status(agent):
    """Print session status"""
    print("\n" + "="*70)
    print("SESSION STATUS")
    print("="*70)
    print(f"  Session ID:    {agent.session_id}")
    print(f"  Customer ID:   {agent.customer_id}")
    print(f"  Agent Name:    {agent.name}")
    print(f"  Elasticsearch: {agent.es_url}")
    print(f"  MCP Gateway:   {agent.mcp_gateway_url or 'Not configured'}")
    print(f"  Conversation:  {len(agent.context.get('conversation_history', []))} turns")
    print("="*70 + "\n")


def main():
    """Main REPL loop"""

    # Print banner
    print_banner()

    # Get session info
    session_id = input("Enter session ID (press Enter for new session): ").strip()
    if not session_id:
        session_id = f"session_{int(datetime.utcnow().timestamp())}"
        print(f"Created new session: {session_id}\n")

    customer_id = input("Enter customer ID (press Enter for 'anonymous'): ").strip()
    if not customer_id:
        customer_id = "anonymous"

    print("\nInitializing agent...")

    # Initialize agent
    try:
        agent = SimpleCustomerSupportAgent(
            session_id=session_id,
            customer_id=customer_id
        )
        print("✓ Agent initialized successfully\n")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. ES_URL and ES_API_KEY are set in config/.env")
        print("  2. Elasticsearch is accessible")
        print("  3. Run 'python infra/elasticsearch_setup.py' first")
        sys.exit(1)

    # REPL loop
    print("Ready! Ask me anything...\n")

    while True:
        try:
            # Get user input
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for using Customer Support Agent!")
                print(f"Session {session_id} saved.\n")
                break

            elif user_input.lower() == 'help':
                print_help()
                continue

            elif user_input.lower() == 'analytics':
                print_analytics(agent)
                continue

            elif user_input.lower() == 'status':
                print_status(agent)
                continue

            elif user_input.lower() == 'clear':
                agent.context["conversation_history"] = []
                print("\n✓ Conversation history cleared\n")
                continue

            # Process query
            print("\nThinking...\n")

            try:
                response = agent.handle_customer_query(user_input)
                print(f"Agent: {response}")

            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"\n✗ Error: {e}")
                print("The agent encountered an error. Please try again.")

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!\n")
            break

        except EOFError:
            print("\n\nSession ended. Goodbye!\n")
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)

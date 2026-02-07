markdown# Investment Analysis Multi-Agent System

An intelligent investment analysis system powered by multi-agent AI that provides comprehensive stock analysis by combining financial metrics and recent news to deliver actionable investment recommendations.

## 🎯 What This Does

This system uses **three specialized AI agents** working together to analyze stocks:

1. **Finance Research Agent** - Retrieves financial metrics (valuation, profitability, growth, health, risk)
2. **News Research Agent** - Fetches recent news and market sentiment
3. **Investment Analyst Agent** - Synthesizes data from both agents to provide:
   - 3 Key Strengths
   - 3 Key Risks
   - Valuation Assessment
   - News Impact Analysis
   - Final Rating (Buy/Hold/Sell) with justification

## 🏗️ Architecture

**Framework:** [AutoGen](https://microsoft.github.io/autogen/) (Microsoft's multi-agent framework)

**Agent Communication:** Round-robin group chat pattern (max 3 turns)

**LLM Provider:** Google Gemini 2.5 Flash

**Data Sources:** 
- Yahoo Finance (yfinance) for financial metrics
- Yahoo Finance News API for market news

**API Framework:** FastAPI

## 🚀 Quick Start

### Prerequisites
- Docker installed
- Internet connection (for API calls to Gemini and Yahoo Finance)

### Option 1: Pull from Docker Hub
```bash
# Pull the image
docker pull ashfaqgg3/autogenagent

# Run the container
docker run -d -p 8000:8000 -e GEMINI_API_KEY=your_gemini_api_key_here ashfaqgg3/autogenagent

#After running establish the uvicorn link using localhost (localhost:uvicornlink)

## 📝 API Usage

### Endpoint: `/chat` (or your actual endpoint name)
```bash
# Example: Ask about a stock
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I invest in Apple?"}'
```

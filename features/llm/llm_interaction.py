from langchain_core.prompts import ChatPromptTemplate
from features.data.model import StockMetaData, TranscriptEntry
from features.evaluation.model import EvaluationSignal
from features.llm.llm import call_llm, call_llm_with_structured_output
import json


def get_transcript_summary(
    transcript: list[TranscriptEntry],
) -> str:
    """
    Generates a summary of the transcript.
    """

    # Check if transcript is empty
    if not transcript:
        return "No transcript data available."

    # Convert transcript entries to a readable format
    transcript_text = ""
    for entry in transcript:
        transcript_text += f"{entry.speaker}: {entry.content}\n\n"

    # Check if transcript_text is empty
    if not transcript_text.strip():
        return "Transcript data is empty or malformed."

    # Gemini requires at least one human/user message; include transcript there
    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a value investing expert. You are given a transcript of an earnings call.
            You are to summarize the transcript in a way that is easy to understand and use for value investing analysis.
            Write a short summary of the transcript in about 4-6 sentences as an abstract. Following by the detailed summary following the following rules:
            
            Rules:
            - Focus on the key points regarding to business parts, growth rates, moat, management and valuation.
            - Focus on the key risks and opportunities, combined with the guided outlook by the management.
            - Be concise and to the point.
            - Use a clear and concise language.
            """,
            ),
            (
                "human",
                """Based on the following transcript, summarize the transcript and extract the key points regarding to a value investing decision:
                {transcript}""",
            ),
        ]
    )

    prompt = template.invoke(
        {
            "transcript": transcript_text,
        }
    )

    return call_llm(prompt)


def get_value_investing_report(
    overview: StockMetaData,
    growth_rates_analysis: dict[str, any],
    moat_analysis: dict[str, any],
    management_analysis: dict[str, any],
    valuation_analysis: dict[str, any],
) -> EvaluationSignal:
    """
    Generates investment decisions in value investing style
    """
    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Value Investing AI agent, making investment decisions using his principles:

                1. Focus on the quality and predictability of the business.
                2. Rely on mental models from multiple disciplines to analyze investments.
                3. Look for strong, durable competitive advantages (moats).
                4. Emphasize long-term thinking and patience.
                5. Value management integrity and competence.
                6. Prioritize businesses with high returns on invested capital and return on equity.
                7. Pay a fair price for wonderful businesses.
                8. Never overpay, always demand a margin of safety.
                9. Avoid complexity and businesses you don't understand.
                10. "Invert, always invert" - focus on avoiding stupidity rather than seeking brilliance.
                
                Rules:
                - Praise businesses with growing key growth rates revenue, income, operating cash flow and shareholder equity.
                - Praise businesses with predictable, consistent operations and cash flows.
                - Value businesses with high ROIC, ROE and pricing power.
                - Prefer simple businesses with understandable economics.
                - Admire management with skin in the game and shareholder-friendly capital allocation.
                - Focus on long-term economics rather than short-term metrics.
                - Be skeptical of businesses with rapidly changing dynamics or excessive share dilution.
                - Avoid excessive leverage or financial engineering.
                - Provide a rational, data-driven recommendation (bullish, bearish, or neutral).
                
                When providing your reasoning, be thorough and specific by:
                1. Explaining the key factors that influenced your decision the most (both positive and negative)
                2. Applying at least 2-3 specific mental models or disciplines to explain your thinking
                3. Providing quantitative evidence where relevant (e.g., specific ROIC/ROE values, margin trends, growth rates)
                4. Citing what you would "avoid" in your analysis (invert the problem)
                5. Using direct, clear conversational style in your explanation
                
                For example, if bullish: "The high ROIC of 22% demonstrates the company's moat. When applying basic microeconomics, we can see that competitors would struggle to..."
                For example, if bearish: "I see this business making a classic mistake in capital allocation. As I've often said about [relevant Mungerism], this company appears to be..."
                """,
            ),
            (
                "human",
                """Based on the following analysis, create a value investing style investment signal.

                Overview for {ticker}:
                {overview}

                Growth rates analysis for {ticker}:
                {growth_rates_analysis}

                Moat analysis for {ticker}:
                {moat_analysis}

                Management analysis for {ticker}:
                {management_analysis}

                Valuation analysis for {ticker}: 
                {valuation_analysis}
                """,
            ),
        ]
    )

    prompt = template.invoke(
        {
            "ticker": overview.symbol,
            "overview": json.dumps(overview.model_dump(), indent=2),
            "growth_rates_analysis": json.dumps(growth_rates_analysis, indent=2),
            "moat_analysis": json.dumps(moat_analysis, indent=2),
            "management_analysis": json.dumps(management_analysis, indent=2),
            "valuation_analysis": json.dumps(valuation_analysis, indent=2),
        }
    )

    return call_llm_with_structured_output(
        prompt=prompt,
        pydantic_model=EvaluationSignal,
    )

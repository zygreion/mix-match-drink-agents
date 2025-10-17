import asyncio
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME="mix_and_match_agent"
USER_ID="penjual_untung"
SESSION_ID="1234"
MODEL_ID="gemini-2.5-flash"

# User personalization
USER_LOCATION = "Jakarta, Indonesia"

# Agents
harga_agent = Agent(
    name="HargaAgent",
    model=MODEL_ID,
    instruction=f"""Jika bahan-bahan {{ingredients_takaran}} tidak valid, langsung keluar dari agent ini.
Sebaliknya, kalkulasi masing-masing prediksi harga bahan di sekitar tempat tinggal pengguna {USER_LOCATION}.
*Jangan menampilkan harga satuan yang umum dijual*
Berikan estimasi total harga per bahan dan total harga semua bahan dalam format tabel
| Bahan | Takaran Saji | Estimasi Harga |
*Estimasi harga adalah estimasi harga bahan per produk yang akan dibuat*
.""",
    output_key="ingredients_prices",
)

takaran_agent = Agent(
    name="TakaranAgent",
    model=MODEL_ID,
    instruction=f"""User menginput bahan-bahan minuman
**Contoh Input**
Jeruk, ada rasa susu, lemon

Berikan satu nama menu minuman paling terkait yang menggunakan bahan yang diberikan
Jika tidak ada minuman yang menggunakan bahan-bahan tersebut, kembali dan tampilkan **ERROR Tidak Ditemukan**

Beserta takaran saji dari masing-masing bahan yang digunakan.
Jika user tidak menginput bahan seperti penggunaan air putih, es batu, dsb yang pasti akan digunakan maka tambahkan ke output dan nanti kalkulasi harganya juga.""",
    output_key="ingredients_takaran",
)

mix_match_agent = SequentialAgent(
    name="MixMatchAgent",
    sub_agents=[takaran_agent, harga_agent]
)

async def main():
    """Main function to run the agent asynchronously."""
    # Session and Runner Setup
    session_service = InMemorySessionService()
    # Use 'await' to correctly create the session
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    runner = Runner(agent=mix_and_match_agent, app_name=APP_NAME, session_service=session_service)

    # Agent Interaction
    query = "mix and match minuman"
    print(f"User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # The runner's run method handles the async loop internally
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response:", final_response)

# Standard way to run the main async function
if __name__ == "__main__":
    asyncio.run(main())

root_agent = mix_match_agent
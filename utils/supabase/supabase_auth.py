from supabase import create_client, Client
import supabase
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
redirect_url = 'http://localhost:8050/'
supabase: Client = create_client(url, key)

def signInWithGithub():
    datahh = supabase.auth.sign_in_with_oauth({
     "provider": 'github',
     "options": {
        "redirect_to": redirect_url
      }
    })
    print(datahh)

def getUser():
    return supabase.auth.get_user()


def get_data():
    try:
      response = (
        supabase.table("dashlinks")
        .select("link", "linkname", "tags", "folder")
        .eq("username", "Fabo011")
        .execute()
      )
      print(response)
    except Exception as e:
      print(e)
    data = response.data
    return data
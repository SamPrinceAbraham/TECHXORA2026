import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = None

if url and key:
    supabase = create_client(url, key)

def ensure_bucket(bucket_name):
    """
    Ensure a bucket exists in Supabase.
    """
    if not supabase:
        return
    try:
        # Check if bucket exists
        buckets = supabase.storage.list_buckets()
        exists = any(b.name == bucket_name for b in buckets)
        if not exists:
            # Create bucket if it doesn't exist (public=True)
            supabase.storage.create_bucket(bucket_name, options={"public": True})
            print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"Error ensuring bucket '{bucket_name}': {e}")

def upload_file(bucket_name, file_path, remote_path):
    """
    Upload a local file to a Supabase bucket.
    Returns the public URL of the uploaded file.
    """
    if not supabase:
        print("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY.")
        return None

    ensure_bucket(bucket_name)

    with open(file_path, 'rb') as f:
        supabase.storage.from_(bucket_name).upload(
            path=remote_path,
            file=f,
            file_options={"cache-control": "3600", "upsert": "true"}
        )
    
    # Get public URL
    public_url = supabase.storage.from_(bucket_name).get_public_url(remote_path)
    return public_url

def upload_bytes(bucket_name, file_bytes, remote_path, content_type="application/pdf"):
    """
    Upload bytes directly to a Supabase bucket.
    """
    if not supabase:
        return None

    ensure_bucket(bucket_name)

    # If file_bytes is a BytesIO object, get the raw bytes
    data = file_bytes.getvalue() if hasattr(file_bytes, 'getvalue') else file_bytes

    supabase.storage.from_(bucket_name).upload(
        path=remote_path,
        file=data,
        file_options={"cache-control": "3600", "upsert": "true", "content-type": content_type}
    )
    
    public_url = supabase.storage.from_(bucket_name).get_public_url(remote_path)
    
    # Append cache-busting timestamp
    import time
    t = int(time.time())
    if "?" in public_url:
        public_url += f"&t={t}"
    else:
        public_url += f"?t={t}"
        
    return public_url


def delete_file(bucket_name, remote_path):
    """
    Delete a file from a Supabase bucket.
    """
    if not supabase:
        return False
        
    try:
        supabase.storage.from_(bucket_name).remove([remote_path])
        return True
    except Exception as e:
        print(f"Error deleting {remote_path} from {bucket_name}: {e}")
        return False

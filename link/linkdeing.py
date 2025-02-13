from flask import Flask, redirect, request, jsonify
import requests

app = Flask(__name__)

LINKEDIN_CLIENT_ID = '77yg6leei8ip5y'
LINKEDIN_CLIENT_SECRET = 'WPL_AP1.pdLxnGVULcLao5iJ.LeRD2w=='
LINKEDIN_REDIRECT_URI = 'http://localhost:5000/linkedin/callback'

@app.route('/linkedin/authorize', methods=['GET'])
def linkedin_authorize():
    """ Step 1: Redirect to LinkedIn's OAuth 2.0 authorization page """
    authorization_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={LINKEDIN_CLIENT_ID}&redirect_uri={LINKEDIN_REDIRECT_URI}"
        f"&scope=w_member_social"
    )
    return redirect(authorization_url)

@app.route('/linkedin/callback', methods=['GET'])
def linkedin_callback():
    """ Step 2: LinkedIn will redirect here with the authorization code """
    authorization_code = request.args.get('code')
    if not authorization_code:
        return jsonify({"error": "Authorization code not provided"}), 400

    # Step 3: Exchange authorization code for an access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': LINKEDIN_REDIRECT_URI,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET
    }
    response = requests.post(token_url, data=payload, headers=headers)
    access_token_data = response.json()

    if response.status_code != 200:
        return jsonify({
            "error": access_token_data.get('error', 'Unknown error'),
            "error_description": access_token_data.get('error_description', 'No description provided')
        }), 400

    access_token = access_token_data.get("access_token")
    if not access_token:
        return jsonify({"error": "Failed to get access token"}), 400

    # Step 4: Call post_to_company_page to post on LinkedIn
    company_id = 'M4kLJ08fHH'  # Replace with your company's LinkedIn organization ID
    post_text = "Hello LinkedIn from Python and Flask!"
    status_code, post_response = post_to_company_page(access_token, company_id, post_text)

    return jsonify({
        "status_code": status_code,
        "post_response": post_response
    }), 200

def post_to_company_page(access_token, company_id, post_text):
    """ Step 4: Post the content to the LinkedIn company page """
    url = f"https://api.linkedin.com/v2/ugcPosts"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json',
    }
    payload = {
        "author": f"urn:li:organization:{company_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()

if __name__ == '__main__':
    app.run(debug=True)
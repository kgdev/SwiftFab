#!/usr/bin/env python3
"""
Flexible Fabworks tRPC API client with authentication support
"""

import requests
import json
import sys

class FabworksAPIClient:
    def __init__(self, cookies=None):
        """
        Initialize the Fabworks API client
        
        Args:
            cookies (str): Cookie string from authenticated browser session
        """
        self.base_url = "https://www.fabworks.com/api/trpc"
        self.cookies = cookies or self._get_default_cookies()
        self.session = requests.Session()
        
        # Set default headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.fabworks.com/quotes/qte_333at6zprvFFBYez5eCTxVmFGYl",
            "Cookie": self.cookies,
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
    
    def _get_default_cookies(self):
        """Default authenticated cookies"""
        return "__client_uat=0; __client_uat_vqM_EC95=0; rl_anonymous_id=RS_ENC_v3_ImRjYjM2YWE1LTVjM2ItNDBhNi1iNThiLWNlNjA4MjJmZDJhYiI%3D; rl_page_init_referrer=RS_ENC_v3_IiRkaXJlY3Qi; _gcl_au=1.1.1527406300.1757810490; intercom-id-nejq35td=cea6217e-db32-4966-a3c5-099aa351648e; intercom-session-nejq35td=; intercom-device-id-nejq35td=36534535-9545-42d9-a616-0865f818e419; __stripe_mid=22609d47-c376-4ed8-84bc-706d28de96f02ff400; ph-identify=019945ab-7347-7923-8007-6bd3cdb6d509; h3=Fe26.2**da4c669ad50f5e588fcb4d36a749fb658dd2f2af5c384c3e68f14657437def56*TgerIYpVufI3BMo229Lilw*Q8VgwbJI8U4vs8cUrscEMaXLxiHbBNSc5GCMwUZwEeQeeLILWn3CVLJL3XGQqenzRtJaqlXcwMfKSXnJkH96154_AFSz6FBkIEJzz_3nt3fzq-uoLb92JS5VFiFI8xvr**cfa7832b482c84241e1e2df8a50b7bb6d8310dd54b0228886b0b62f1f38bca52*638HCyldZ7rozOl-n_z-attyOlzz6NDeQsKpVWCDeF8; __stripe_sid=96216296-c4fc-4435-ae86-fcc2c2484ddbf1fdb5; rl_session=RS_ENC_v3_eyJpZCI6MTc1ODYwNzA4NDk3MCwiZXhwaXJlc0F0IjoxNzU4NjA4ODg0OTc4LCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; ph_phc_Kzw3uJ6aZnnHiIM4wE2nooqdpIxq3CjxCrpT8vUH2dS_posthog=%7B%22distinct_id%22%3A%22019945ab-7347-7923-8007-6bd3cdb6d509%22%2C%22%24sesid%22%3A%5B1758607135118%2C%2201997501-7b4d-71f0-bfa9-37372196d0c4%22%2C1758604655437%5D%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22%24direct%22%2C%22u%22%3A%22https%3A%2F%2Fwww.fabworks.com%2F%22%7D%7D"
    
    def call_trpc_method(self, method_name, data, batch=True):
        """
        Generic method to call any tRPC endpoint
        
        Args:
            method_name (str): The tRPC method name (e.g., 'parts.update')
            data (dict or list): The data to send. If list, each item will be batched
            batch (bool): Whether to use batch format
        
        Returns:
            requests.Response: The response object
        """
        if batch:
            url = f"{self.base_url}/{method_name}?batch=1"
            
            # Handle multiple data items for true batching
            if isinstance(data, list):
                payload = {}
                for i, item in enumerate(data):
                    payload[str(i)] = {"json": item}
            else:
                # Single item
                payload = {"0": {"json": data}}
        else:
            url = f"{self.base_url}/{method_name}"
            payload = data
        
        try:
            print(f"🚀 Calling tRPC method: {method_name}")
            print(f"🎯 URL: {url}")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload, headers=self.headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"📄 Response: {json.dumps(response_data, indent=2)}")
                
                if response.status_code == 200:
                    print("✅ API call successful!")
                    return response_data
                else:
                    print(f"❌ API call failed with status: {response.status_code}")
                    
            except ValueError:
                print(f"📄 Non-JSON Response: {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    
    def update_parts_batch(self, part_updates):
        """
        Update multiple parts in a single batched tRPC call (MOST EFFICIENT)
        
        Args:
            part_updates (list): List of dictionaries, each containing:
                - 'part_id': The part ID to update
                - 'updates': Dictionary of fields to update
                Example: [
                    {'part_id': 'part_123', 'updates': {'materialThickness': '0.25'}},
                    {'part_id': 'part_456', 'updates': {'materialThickness': '0.125', 'finish': 'Deburred'}}
                ]
        
        Returns:
            Single API response containing results for all updates
        """
        print(f"🚀 Batching {len(part_updates)} part updates into single API call...")
        
        # Prepare batch data
        batch_data = []
        for part_update in part_updates:
            update_data = {"id": part_update['part_id'], **part_update['updates']}
            batch_data.append(update_data)
        
        print(f"📦 Batch contains {len(batch_data)} part updates")
        
        # Make single batched API call
        result = self.call_trpc_method("parts.update", batch_data)
        
        print(f"✅ Batch update completed with single API call!")
        return result
    
    def update_single_part(self, part_id, updates):
        """
        Update a single part using sequential API call
        
        Args:
            part_id (str): The part ID to update
            updates (dict): Dictionary of fields to update
        
        Returns:
            API response for the single part update
        """
        print(f"🔄 Updating single part: {part_id}")
        
        # Prepare update data
        update_data = {"id": part_id, **updates}
        
        # Make single API call (non-batch)
        result = self.call_trpc_method("parts.update", update_data, batch=True)
        
        print(f"✅ Single part update completed!")
        return result

    def update_multiple_parts(self, part_updates):
        """
        Update multiple parts using sequential API calls (instead of batch)
        
        Args:
            part_updates (list): List of dictionaries, each containing:
                - 'part_id': The part ID to update
                - 'updates': Dictionary of fields to update
                Example: [
                    {'part_id': 'part_123', 'updates': {'materialThickness': '0.25'}},
                    {'part_id': 'part_456', 'updates': {'materialThickness': '0.125', 'finish': 'Deburred'}}
                ]
        
        Returns:
            List of API responses for each part update
        """
        print(f"🔄 Updating {len(part_updates)} parts using sequential API calls...")
        
        results = []
        for i, part_update in enumerate(part_updates, 1):
            print(f"📝 Processing part {i}/{len(part_updates)}: {part_update['part_id']}")
            
            # Update single part
            result = self.update_single_part(part_update['part_id'], part_update['updates'])
            results.append(result)
            
            # Add small delay between calls to avoid overwhelming the server
            # import time
            # time.sleep(0.1)
        
        print(f"✅ Sequential updates completed for {len(part_updates)} parts!")
        return results
    
    def update_all_parts_in_quote(self, quote_id, updates):
        """
        Update all parts in a quote with the same parameters using sequential API calls
        
        Args:
            quote_id (str): The quote ID to get parts from
            updates (dict): Dictionary of fields to update (applied to all parts)
        
        Returns:
            Dictionary containing:
            - 'quote_details': The original quote details
            - 'part_updates': Sequential update results
            - 'summary': Summary of the updates
        """
        print(f"🔍 Getting parts from quote: {quote_id}")
        
        # First, get the quote details to extract part IDs
        quote_response = self.get_quote_details(quote_id)
        
        if not quote_response or not isinstance(quote_response, list) or len(quote_response) == 0:
            return {"error": "Failed to get quote details"}
        
        quote_data = quote_response[0].get('result', {}).get('data', {}).get('json')
        if not quote_data:
            return {"error": "No quote data found"}
        
        # Extract all parts from all assemblies
        all_parts = []
        for assembly in quote_data.get('assemblies', []):
            for part in assembly.get('parts', []):
                all_parts.append(part)
        
        if not all_parts:
            return {"error": "No parts found in quote", "quote_details": quote_data}
        
        print(f"📋 Found {len(all_parts)} parts in quote")
        
        # Create part_updates list for batch update
        part_updates = []
        for part in all_parts:
            part_updates.append({
                'part_id': part['id'],
                'updates': updates
            })
        
        # Show what we're about to update
        print(f"📝 Will apply these updates to all {len(all_parts)} parts:")
        for key, value in updates.items():
            print(f"   - {key}: {value}")
        
        # Update all parts using sequential API calls
        update_results = self.update_multiple_parts(part_updates)
        
        # Create summary - sequential response format
        successful_updates = 0
        failed_updates = 0
        
        if isinstance(update_results, list) and len(update_results) > 0:
            # Count successful results in sequential response
            for result_item in update_results:
                if result_item and hasattr(result_item, 'status_code') and result_item.status_code == 200:
                    successful_updates += 1
                elif isinstance(result_item, dict) and 'result' in result_item:
                    successful_updates += 1
                elif isinstance(result_item, dict) and 'error' in result_item:
                    failed_updates += 1
                else:
                    failed_updates += 1
        else:
            failed_updates = len(all_parts)
        
        summary = {
            'total_parts': len(all_parts),
            'successful_updates': successful_updates,
            'failed_updates': failed_updates,
            'updates_applied': updates
        }
        
        print(f"\n📊 Update Summary:")
        print(f"   ✅ Successful: {successful_updates}")
        print(f"   ❌ Failed: {failed_updates}")
        print(f"   📦 Total parts: {len(all_parts)}")
        
        return {
            'quote_details': quote_data,
            'part_updates': update_results,
            'summary': summary
        }
    
    
    def get_quote_details(self, quote_id):
        """
        Get quote details using GET request with URL parameters
        
        Args:
            quote_id (str): The quote ID to retrieve
        
        Returns:
            The API response
        """
        import urllib.parse
        
        # Create the input parameter as expected by the API
        input_data = {"0": {"json": {"id": quote_id}}}
        encoded_input = urllib.parse.quote(json.dumps(input_data))
        
        url = f"{self.base_url}/quotes.detail?batch=1&input={encoded_input}"
        
        try:
            print(f"🚀 Getting quote details: {quote_id}")
            print(f"🎯 URL: {url}")
            print(f"📦 Input data: {json.dumps(input_data, indent=2)}")
            
            response = self.session.get(url, headers=self.headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"📄 Response: {json.dumps(response_data, indent=2)}")
                
                if response.status_code == 200:
                    print("✅ Quote details retrieved successfully!")
                    return response_data
                else:
                    print(f"❌ Failed to get quote details. Status: {response.status_code}")
                    
            except ValueError:
                print(f"📄 Non-JSON Response: {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

def main():
    """
    Main function with example usage including batch updates
    """
    print("🔧 Fabworks API Client - Batch Update Demo\n")
    
    # Initialize client
    client = FabworksAPIClient()
    
    quote_id = "qte_333at6zprvFFBYez5eCTxVmFGYl"
    
    # Example 1: Get initial quote state
    print("📋 Example 1: Get initial quote details")
    result = client.get_quote_details(quote_id)
    
    print("\n" + "="*70 + "\n")
    
    # Example 2: Update all parts in quote to same material thickness
    print("🚀 Example 2: Update ALL parts to 0.125 inch thickness")
    batch_result = client.update_all_parts_in_quote(
        quote_id=quote_id,
        updates={"materialThickness": "0.125"}
    )
    
    print("\n" + "="*70 + "\n")
    
    # Example 3: Update multiple specific parts with different settings
    print("🎯 Example 3: Update specific parts with different settings")
    specific_updates = [
        {
            'part_id': 'part_335IuS3Jt0XDMU7lmsQQyV84yP3',  # Cube003
            'updates': {'materialThickness': '0.25', 'finish': 'Deburred'}
        },
        {
            'part_id': 'part_335IuW5eTNGSaU3VuBPdDCmcGtQ',  # Cube
            'updates': {'materialThickness': '0.1875'}
        },
        {
            'part_id': 'part_335IuS0nQV4GVsm5YmgtOHfC1Hs',  # Cube005
            'updates': {'materialThickness': '0.375'}
        }
    ]
    
    multi_result = client.update_multiple_parts(specific_updates)
    
    print("\n" + "="*70 + "\n")
    
    # Example 4: Batch update remaining parts
    print("🚀 Example 4: Batch update remaining parts to 0.5 inch")
    remaining_parts = [
        {'part_id': 'part_335IuRN5yY1CJ7WM41BpM7mnqt9', 'updates': {'materialThickness': '0.5'}},  # Cube004
        {'part_id': 'part_335IuUTxABXuZdELzMzpdOKMZzj', 'updates': {'materialThickness': '0.5'}},  # Cube002
        {'part_id': 'part_335IuX8NvqeOVWQv5b11z1iz8WX', 'updates': {'materialThickness': '0.5'}}   # Cube001
    ]
    
    batch_result_2 = client.update_multiple_parts(remaining_parts)
    
    print("\n" + "="*70 + "\n")
    
    # Example 5: Final verification - get updated quote
    print("✅ Example 5: Get final quote state to verify all updates")
    final_result = client.get_quote_details(quote_id)

if __name__ == "__main__":
    main()

# Dynamic Google Scholar Citations

This al-folio website now supports **dynamic Google Scholar citation counts** that update in real-time after the site is built and served. This means visitors will always see the latest citation numbers, even without rebuilding the Jekyll site.

## 🚀 What Changed

### Before
- Citation counts were fetched at build time using a Jekyll plugin
- Once the site was built, citation counts remained static
- Required rebuilding and redeploying the site to update citation counts

### After
- Citation counts show "loading..." initially when the page loads
- JavaScript fetches real-time citation counts from Google Scholar
- Results are cached for 24 hours to improve performance
- No need to rebuild the site to get updated citation counts

## 📋 How It Works

1. **Build Time**: The Jekyll site builds with placeholder citation counts ("loading...")
2. **Page Load**: JavaScript automatically detects Google Scholar citation badges
3. **API Calls**: Fetches current citation counts (with caching and rate limiting)
4. **Updates**: Dynamically updates the badge images with current counts
5. **Caching**: Stores results in browser localStorage for 24 hours

## 🔧 Technical Implementation

### Files Modified
- `_layouts/bib.liquid`: Updated to use placeholders and data attributes
- `_includes/scripts.liquid`: Added the dynamic citation script
- `assets/js/google-scholar-dynamic.js`: New JavaScript file (main implementation)

### Key Features
- **Multiple Fallback Methods**: Tries several CORS proxy services
- **Intelligent Caching**: 24-hour localStorage cache to reduce API calls
- **Error Handling**: Graceful fallback when citation counts can't be fetched
- **Visual Feedback**: Loading indicators and animations
- **Rate Limiting**: Delays between requests to avoid being blocked

## ⚙️ Configuration Options

### Caching Duration
To change how long citation counts are cached:

```javascript
// In assets/js/google-scholar-dynamic.js, line ~8
this.cacheExpiry = 12 * 60 * 60 * 1000; // Change to 12 hours
```

### CORS Proxy Services
The system tries these proxy services in order:
1. `api.allorigins.win` (free, reliable)
2. `corsproxy.io` (free, backup)
3. `cors-anywhere.herokuapp.com` (requires access request)

## 🚨 Limitations & Considerations

### CORS Proxy Reliability
- Free proxy services may have downtime or rate limits
- Google Scholar may block some proxy services
- For high-traffic sites, consider setting up your own backend

### Rate Limiting
- Google Scholar may block requests if too frequent
- The system includes delays between requests
- Consider implementing additional rate limiting for high-volume sites

### Fallback Behavior
- If citation counts can't be fetched, badges show "?"
- Users can still click to view the paper on Google Scholar
- Console logs provide debugging information

## 🏗️ Setting Up Your Own Backend (Recommended)

For production websites with many citations, setting up your own backend API is recommended:

### Option 1: Simple Python Flask API

Create a file `scholar_api.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import random

app = Flask(__name__)
CORS(app)

@app.route('/api/scholar-citations')
def get_citations():
    scholar_id = request.args.get('scholar_id')
    citation_id = request.args.get('citation_id')
    
    url = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={scholar_id}&citation_for_view={scholar_id}:{citation_id}"
    
    # Add delay to avoid being blocked
    time.sleep(random.uniform(1, 3))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Citation-Counter/1.0)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract citation count from meta description
        meta = soup.find('meta', {'name': 'description'})
        if meta:
            content = meta.get('content', '')
            match = re.search(r'Cited by (\d+(?:,\d+)*)', content)
            if match:
                count = int(match.group(1).replace(',', ''))
                return jsonify({'citation_count': count})
        
        return jsonify({'citation_count': 0})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

Install dependencies:
```bash
pip install flask flask-cors requests beautifulsoup4
```

Run the API:
```bash
python scholar_api.py
```

### Option 2: Serverless Functions

Deploy as a serverless function on:
- **Vercel**: Create `api/scholar-citations.js`
- **Netlify**: Create `netlify/functions/scholar-citations.js`
- **AWS Lambda**: Deploy as a Lambda function

### Option 3: Use Existing Services

- **SerpApi**: Paid service with reliable Google Scholar API
- **ScrapingBee**: CORS proxy with better reliability
- **Your own VPS**: Deploy the Flask API on a cloud server

## 🔍 Troubleshooting

### Citations Not Updating

1. **Open browser developer tools** (F12) and check the Console tab
2. Look for error messages related to citation fetching
3. **Clear the cache**:
   ```javascript
   // Run in browser console
   Object.keys(localStorage).forEach(key => {
     if (key.startsWith('scholar_cache_')) {
       localStorage.removeItem(key);
     }
   });
   ```
4. **Refresh the page** and check if citations update

### CORS Errors

If you see CORS-related errors in the console:
1. The proxy services might be down - try again later
2. Consider setting up your own backend API
3. Check if your browser is blocking requests

### Performance Issues

If the page loads slowly due to citation fetching:
1. Reduce the number of citations on a single page
2. Implement lazy loading (fetch only when badges are visible)
3. Increase cache duration to reduce API calls

## 📊 Monitoring & Analytics

To monitor the performance of your dynamic citations:

1. **Browser Console**: Check for error messages and timing
2. **Network Tab**: Monitor API requests and response times
3. **Google Analytics**: Track custom events for citation updates
4. **Backend Logs**: If using your own API, monitor request patterns

## 🔐 Security & Best Practices

1. **Respect Rate Limits**: Don't make too many requests to Google Scholar
2. **Cache Aggressively**: Use localStorage and consider service workers
3. **Error Handling**: Always provide fallbacks when API calls fail
4. **User Experience**: Show loading states and provide feedback
5. **Privacy**: Be transparent about external API calls in your privacy policy

## 🚀 Future Enhancements

Potential improvements to consider:

1. **Service Worker Caching**: Cache API responses for offline access
2. **Batch API Calls**: Fetch multiple citations in a single request
3. **Real-time Updates**: Use WebSockets for live citation updates
4. **A/B Testing**: Compare static vs dynamic citation performance
5. **Analytics Integration**: Track citation view patterns

## 📝 License & Attribution

This implementation is based on the original al-folio Jekyll plugin but enhanced with client-side JavaScript for real-time updates. Please respect Google Scholar's terms of service and implement appropriate rate limiting.

---

For questions or issues with the dynamic citation system, please check the browser console for error messages and refer to this documentation. 
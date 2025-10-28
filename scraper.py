"""
Pain-Matrix Scraper Bot (FREE TIER)
====================================
This bot scrapes Reddit post titles using PRAW (Reddit's official API).
It does NOT use any paid AI APIs - this is the free tier.

For AI-powered insights, users must subscribe to the $29/mo PRO plan.
"""

import os
import praw
from datetime import datetime
import re


def get_env_or_fail(key):
    """Get environment variable or raise error."""
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


def authenticate_reddit():
    """Authenticate to Reddit using PRAW."""
    print("🔐 Authenticating to Reddit...")
    
    reddit = praw.Reddit(
        client_id=get_env_or_fail("REDDIT_CLIENT_ID"),
        client_secret=get_env_or_fail("REDDIT_CLIENT_SECRET"),
        user_agent=get_env_or_fail("REDDIT_USER_AGENT"),
        username=get_env_or_fail("REDDIT_USERNAME"),
        password=get_env_or_fail("REDDIT_PASSWORD")
    )
    
    print(f"✅ Authenticated as: {reddit.user.me()}")
    return reddit


def scrape_subreddit_top_posts(reddit, subreddit_name, limit=5):
    """Scrape top posts from a subreddit."""
    try:
        subreddit = reddit.subreddit(subreddit_name.replace("r/", ""))
        posts = []
        
        for post in subreddit.hot(limit=limit):
            posts.append({
                "title": post.title,
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,
                "comments": post.num_comments
            })
        
        return posts
    except Exception as e:
        print(f"⚠️  Error scraping {subreddit_name}: {str(e)}")
        return []


def format_posts_as_markdown(posts, max_posts=10):
    """Format posts as markdown list."""
    if not posts:
        return "*No posts available at this time.*\n"
    
    markdown = ""
    for i, post in enumerate(posts[:max_posts], 1):
        markdown += f"{i}. **[{post['title']}]({post['url']})** "
        markdown += f"(↑{post['score']} | 💬{post['comments']})\n"
    
    return markdown


def update_readme(new_content):
    """Update the README.md file with new content."""
    readme_path = "README.md"
    
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find and replace the auto-updating section
        # Pattern: between "## Today's Top 10 Trending Titles (Free Feed)" and "---"
        pattern = r"(## Today's Top 10 Trending Titles \(Free Feed\))(.*?)(---\n\n### About This Bot)"
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        replacement = f"\\1\n\n{new_content}\n*Last updated: {timestamp}*\n\n\\3"
        
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"✅ README.md updated successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Failed to update README.md: {str(e)}")
        return False


def main():
    """Main execution function."""
    print("=" * 60)
    print("PAIN-MATRIX SCRAPER BOT (FREE TIER)")
    print("=" * 60)
    
    # Get configuration from environment
    niche_name = get_env_or_fail("NICHE_NAME")
    target_subreddits = get_env_or_fail("TARGET_SUBREDDITS")
    subreddit_list = [s.strip() for s in target_subreddits.split(",")]
    
    print(f"📊 Niche: {niche_name}")
    print(f"🎯 Target Subreddits: {', '.join(subreddit_list)}")
    
    # Authenticate to Reddit
    reddit = authenticate_reddit()
    
    # Scrape posts from all target subreddits
    all_posts = []
    for subreddit in subreddit_list:
        print(f"\n📥 Scraping {subreddit}...")
        posts = scrape_subreddit_top_posts(reddit, subreddit, limit=5)
        all_posts.extend(posts)
        print(f"   ✓ Found {len(posts)} posts")
    
    # Sort by score (engagement) and take top 10
    all_posts.sort(key=lambda x: x["score"], reverse=True)
    top_posts = all_posts[:10]
    
    print(f"\n📊 Total posts collected: {len(all_posts)}")
    print(f"📌 Top posts to display: {len(top_posts)}")
    
    # Format as markdown
    markdown_content = format_posts_as_markdown(top_posts)
    
    # Update README.md
    print("\n📝 Updating README.md...")
    update_readme(markdown_content)
    
    print("\n" + "=" * 60)
    print("✅ SCRAPING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

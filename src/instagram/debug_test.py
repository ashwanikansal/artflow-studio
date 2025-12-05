from src.instagram.service import get_my_posts, get_post_insights, get_post_comments

def main():
    print("Fetching Instagram posts...")
    posts = get_my_posts(limit=10)
    
    for p in posts:
        print("*" * 20)
        print("Post_id: ", p.id)
        print("Type: ", p.type)
        print("Likes: ", p.likes)
        print("Comments count: ", p.comments_count)
        print("Created at: ", p.created_at)
        print("Caption: ", p.caption[:60], "...\n")
        # print(p.id, p.type, p.likes, p.comments_count, p.created_at, 'caption:', p.caption[:60])

    print("\nFetching insights and comments for the first post...")

    if posts:
        first = posts[0]
        insights = get_post_insights(first.id)
        print("\nInsights for first post:", insights)

        comments = get_post_comments(first.id)
        print("\nComments for first post:")
        for c in comments:
            print(c.id, c.text)

if __name__ == "__main__":
    main()

from src.instagram.service import get_my_posts, get_post_insights, get_post_comments

def main():
    posts = get_my_posts(limit=5)
    print("Posts:")
    for p in posts:
        print(p.id, p.type, p.likes, p.comments_count)

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

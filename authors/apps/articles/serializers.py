from rest_framework import serializers
from .models import Articles
from authors.apps.authentication.models import User


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Articles
        fields = ("__all__")

    @staticmethod
    def get_all_objects():
        articles = Articles.objects.all()
        user = AuthorSerializer()

        articles_list = []
        for article in articles:
            article = {
                "slug": article.slug,
                "title": article.title,
                "description": article.description,
                "body": article.body,
                "tagList": article.tagList.split(","),
                "createdAt": article.createdAt,
                "updatedAt": article.updatedAt,
                "favorited": article.favorited,
                "favoritesCount": article.favoritesCount,
                "author": user.get_author_objects(article.author.pk)
            }
            articles_list.append(article)

        return (articles_list)

    def get_specific_objects(self, slug):
        self.article = Articles.objects.get(slug=slug)
        user = AuthorSerializer()
        article = {
            "slug": self.article.slug,
            "title": self.article.title,
            "description": self.article.description,
            "body": self.article.body,
            "tagList": self.article.tagList.split(","),
            "createdAt": self.article.createdAt,
            "updatedAt": self.article.updatedAt,
            "favorited": self.article.favorited,
            "favoritesCount": self.article.favoritesCount,
            "author": user.get_author_objects(self.article.author.pk)
        }

        return (article)

    def posting_articles(self, value):  # dictionary passed from view
        author_details = self.get_authors_object(
            value['author'])  # get user object
        article_slug = self.slugify_string(value['title'])
        read_time = self.readTime(value['body'])

        self.new_article = Articles(
            slug=article_slug,
            title=value['title'],
            description=value['description'],
            body=value['body'],
            tagList=value['tagList'],
            author=author_details,
            readtime=read_time)

        try:
            self.new_article.save()
            return (self.get_all_objects())

        except Exception as What_is_this:
            print('error {}'.format(What_is_this))
            return ("Could not post")

    def get_authors_object(self, name):
        user_details = User.objects.get(username=name)
        return user_details

    def slugify_string(self, string):
        string = string.lower()
        processed_slug = string.replace(" ", "-")

        db_check = Articles.objects.filter(slug=processed_slug).count()
        if db_check < 1:  # Slug exists in DB
            return processed_slug

        else:
            new_slug = '{}*'.format(processed_slug)
            return self.slugify_string(new_slug)

    def readTime(self, story):
        story_list = story.split(" ")
        resolved_time = (len(story_list)) / 200
        read_time = round(resolved_time)
        return read_time

    def updateArticle(self, value, passed_slug):
        try:
            Articles.objects.filter(
                slug=passed_slug).update(
                slug=self.slugify_string(
                    value['title']),
                title=value['title'],
                description=value['description'],
                body=value['body'],
                tagList=value['tagList'],
                readtime=self.readTime(
                    value['body']))
            return ('Update was successful, Title: {}'.format(value['title']))

        except Exception as What_is_this:
            print('Received error is : {}'.format(What_is_this))
            return ('error')

    def deleteArticle(self, passed_slug):
        try:
            deleted_article = Articles.objects.get(slug=passed_slug)
            title = deleted_article.title
            deleted_article.delete()
            return('Article title: {} deleted successfully'.format(title))

        except Exception as What_is_this:
            print('Received error is : {}'.format(What_is_this))
            return ("Article does not exist")


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("__all__")

    def get_author_objects(self, id):
        user = User.objects.get(pk=id)

        author = {
            'username': user.username,
            'bio': 'profile.bio',
            'image': 'profile.image',
            # 'following': profile.following
        }
        return (author)

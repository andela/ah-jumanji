from django.db import models
from django.db.models import Count

# local imports
from authors.apps.articles.models import Articles
from authors.apps.profiles.models import Profile

# Create your models here.


class Rating(models.Model):

    # rating ranges
    ratings_range = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )

    rating = models.IntegerField(choices=ratings_range, default=0)
    rater = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('article', 'rater')

    @staticmethod
    def get_average_rating(article_id):

        queryset = Rating.objects.filter(
            article_id=article_id).values('rating').annotate(
            raters=Count('rating'))
        # check if ratings exists
        if not queryset:
            return "Article has no ratings"

        ratings = []
        raters = []
        for data in queryset:
            # get number of votes per rating
            ratings.append(data['rating'] * data['raters'])
            raters.append(data['raters'])  # gets raters count

        average_rating = round(sum(ratings) / sum(raters), 1)

        return average_rating

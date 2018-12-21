from django.urls import reverse
from django_social_share.templatetags import social_share

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User


class ShareArticleView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        provider = kwargs['provider']
        example_providers = ['facebook', 'email', 'twitter']

        if provider not in example_providers:
            return Response(
                {
                    'error': 'provider link is invalid',
                }, status.HTTP_400_BAD_REQUEST)

        try:
            article = Articles.objects.get(slug=kwargs['slug'])

        except Exception as error:
            print('Received error is : {}'.format(error))
            return Response({"message": "Article does not exist"},
                            status.HTTP_404_NOT_FOUND)

        article_link = request.build_absolute_uri(
            reverse('articleSpecific', kwargs={'slug': article.slug})
            )

        context = {'request': request}
        text = "Daily Digest from Authors Haven"
        user = User.objects.get(id=article.author_id).username
        subject = "Read: {} by {} from Authors Haven".format(
                                                                article.title,
                                                                user)
        if provider == 'email':
            link = social_share.send_email_url(
                                                context,
                                                subject,
                                                text,
                                                article_link)['mailto_url']
            return Response(
                            {'link': link, 'provider': provider},
                            status=status.HTTP_200_OK)
        return Response(
                        {
                            'link': self.set_link(
                                                    context,
                                                    provider,
                                                    article_link, args),
                            'provider': provider}, status.HTTP_200_OK)

    def set_link(self, context, provider, article_link, *args):
        providers = {
            "twitter": [social_share.post_to_twitter_url, "tweet_url"],
            "facebook": [social_share.post_to_facebook_url, "facebook_url"]
            }
        provider_link = providers.get(provider, providers['facebook'])
        return provider_link[0](context, article_link)[provider_link[1]]

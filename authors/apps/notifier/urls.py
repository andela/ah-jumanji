from django.urls import path

from authors.apps.notifier.views import GetMailingList, \
    ViewUpdateMailingList, \
    GetNotifications, ReadNotifications, MarkNotificationsAsRead, \
    GetReadNotifications, UnreadNotification

urlpatterns = [
    path('mailing_list/', GetMailingList.as_view(), name="mailing-list"),
    path('mailing_status/',
         ViewUpdateMailingList.as_view(),
         name="mailing-list-status"),
    path('notifications/unread', GetNotifications.as_view(),
         name='notifications'),
    path('notifications/read', GetReadNotifications.as_view(),
         name='marked-as-read-notifications'),
    path('notifications/mark_read', MarkNotificationsAsRead.as_view(),
         name='mark-notifications-read'),
    path('notifications/<int:id>', ReadNotifications.as_view(),
         name='read-notification'),
    path('notifications/unmark/<int:id>', UnreadNotification.as_view(),
         name='mark-notification-read')
]

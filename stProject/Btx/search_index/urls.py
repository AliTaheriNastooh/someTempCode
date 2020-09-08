from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from search_index.viewsets.post import PostDocumentView

router = DefaultRouter()
posts = router.register(r'posts',
                        PostDocumentView,
                        basename='postdocument')
urlpatterns = [
    url(r'^', include(router.urls)),
]


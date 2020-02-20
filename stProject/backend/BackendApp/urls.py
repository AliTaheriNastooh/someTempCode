from rest_framework.routers import SimpleRouter

from BackendApp import views


app_name = 'BackendApp'

router = SimpleRouter()
router.register(
    prefix=r'',
    basename='posts',
    viewset=views.PostViewSet
)
urlpatterns = router.urls
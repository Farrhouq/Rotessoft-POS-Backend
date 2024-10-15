from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, ProductViewSet, ProductSaleViewSet, SaleViewSet, DashboardView, NewBusinessRegistrationView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

router = DefaultRouter()

router.register(r"store", StoreViewSet)
router.register(r"product", ProductViewSet)
router.register(r"productsale", ProductSaleViewSet)
router.register(r"sale", SaleViewSet)


urlpatterns = router.urls

urlpatterns += [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('register/', NewBusinessRegistrationView.as_view(), name='new'),
]

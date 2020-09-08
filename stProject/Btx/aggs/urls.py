from django.urls import path
from .views import stock_count_by_date, stock_count_by_person, stock_count_in_channel, channel_count_by_stock, person_count_by_stock

urlpatterns = [
    path("count/date", stock_count_by_date, name="CountStockFromDate"),
    path("count/sender", stock_count_by_person, name="CountStockByPerson"),
    path("count/channel", stock_count_in_channel, name="CountStockByChannel"),
    path("count/channelByStock", channel_count_by_stock, name="CountChannelByStock"),
    path("count/personByStock", person_count_by_stock,name="PersonByStockCount")

]
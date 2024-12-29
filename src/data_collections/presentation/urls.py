from django.urls import path
from .views import CSVDownloadView, CollectionsList, DatasetFetchView, CollectionDetails, generate_pdf_view, generate_pdf_with_chart_view
from django.views.generic.base import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/collections/')),
    path('collections/', CollectionsList.as_view()),
    path('collections/<int:id>', CollectionDetails.as_view()),
    path('fetch-dataset/', DatasetFetchView.as_view()),
    path('fetch-dataset/<int:id>', DatasetFetchView.as_view()),
    path('download/<str:filename>/', CSVDownloadView.as_view(), name='csv_download'),
    path('generate-pdf/<str:filename>/', generate_pdf_view, name='generate_pdf'),
    path('generate-chart-pdf/<str:filename>/', generate_pdf_with_chart_view, name='generate_chart_pdf')
]


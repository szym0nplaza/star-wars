import os
import csv
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from matplotlib import pyplot as plt
from django.conf import settings
from django.http import FileResponse
from data_collections.infrastructure.ext import CollectionsHandler, DBRepository
from data_collections.application.services import CollectionsService


class CollectionsList(TemplateView):
    template_name = "list.html"
    _handler = CollectionsService(
        data_handler=CollectionsHandler(), repo=DBRepository()
    )

    def get(self, request):
        db_data = self._handler.get_db_data()
        return render(request, self.template_name, context={"collections": db_data})


class DatasetFetchView(View):
    _handler = CollectionsService(
        data_handler=CollectionsHandler(), repo=DBRepository()
    )

    def get(self, _request):
        self._handler.retirieve_ext_data()
        return JsonResponse({"message": "ok"})


class CollectionDetails(TemplateView):
    template_name = "collection-details.html"
    _handler = CollectionsService(
        data_handler=CollectionsHandler(), repo=DBRepository()
    )

    def get(self, request, id):
        records_count = int(request.GET.get("records"))
        filters = request.GET.get("filters")
        dto = self._handler.get_csv_data(id, records_count, filters)
        return render(
            request,
            self.template_name,
            context={
                **dto.__dict__,
                "dataset_id": id,
                "chosen_filters": filters,
            },
        )

class CSVDownloadView(View):
    def get(self, request, filename):
        # Define the directory where the CSV files are stored
        csv_dir = os.path.join(settings.BASE_DIR, 'static', 'datasets')  # Adjust the path as per your setup
        file_path = os.path.join(csv_dir, filename)

        # Serve the file as a download
        response = FileResponse(open(file_path, 'rb'), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def generate_pdf_view(request, filename):
    csv_file_path = os.path.join(settings.BASE_DIR, 'static', 'datasets', filename)
    headers = []
    dataset = []
    try:
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)
            dataset = list(csv_reader)
    except FileNotFoundError:
        return HttpResponse("CSV file not found.", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

    html_content = render_to_string('pdf_template.html', {'headers': headers, 'dataset': dataset})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="table.pdf"'

    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse("An error occurred while generating the PDF.", status=500)

    return response


def generate_pdf_with_chart_view(request, filename):
    csv_file_path = os.path.join(settings.BASE_DIR, 'static', 'datasets', filename)
    headers = []
    dataset = []

    try:
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader)
            dataset = list(csv_reader)
    except FileNotFoundError:
        return HttpResponse("CSV file not found.", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

    # Generate Chart
    heights = [int(row[1]) for row in dataset if row[1].isdigit()]  # Assume second column is "height"
    names = [row[0] for row in dataset]  # Assume first column is "name"

    plt.figure(figsize=(10, 6))
    plt.bar(names[:10], heights[:10], color='skyblue')  # Limit to 10 items for readability
    plt.title("Top 10 Characters by Height")
    plt.xlabel("Character Name")
    plt.ylabel("Height (cm)")
    os.makedirs(os.path.join(settings.BASE_DIR, 'static', 'charts'), exist_ok=True)
    chart_path = os.path.join(settings.BASE_DIR, 'static', 'charts', f'{filename}.png')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    # Render HTML with the chart and table
    html_content = render_to_string('pdf_chart_template.html', {
        'headers': headers,
        'dataset': dataset,
        'chart_path': chart_path,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="chart_table.pdf"'

    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse("An error occurred while generating the PDF.", status=500)

    return response

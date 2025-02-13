# resources.py
from import_export import resources
from .models import foreclosure_Events

class ForeclosureEventsResource(resources.ModelResource):
    class Meta:
        model = foreclosure_Events
        import_id_fields = ('id',)
        exclude = [
            'efl_updated_from',
            'efl_updated_to',
            'tax_sale_next',
            'tax_sale_updated_from',
            'tax_sale_updated_to',
            'mortgage_sale_next',
            'mortgage_sale_updated_from',
            'mortgage_sale_updated_to'
            ]

        # fields = [
        #     'id',
        #     'state',
        #     'county',
        #     'population',
        #     'recorder',
        #     'assessor',
        #     'tax_collector',
        #     'gis',
        #     'district',
        #     'civil',
        #     'municipal',
        #     'probate',
        #     'superior',
        #     'supreme',
        #     'surrogate',
        #     'excess_funds_list',
        #     'tax_sale',
        #     'tax_sale_data_status',
        #     'tax_sale_case_search',
        #     'mortgage_sale',
        #     'mortgage_sale_data_status',
        #     'mortgage_sale_case_search',
        #     'public_notice'
        #     ]

    

class ForeclosureEventsExportResource(resources.ModelResource):
    class Meta:
        model = foreclosure_Events

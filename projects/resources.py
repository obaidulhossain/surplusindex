# from import_export import resources
# from propertydata.models import *
# from django.forms import ModelForm

# class PropertyModelResource(resources.ModelResource):
#     class Meta:
#         model = Property
# class PropertyModelForm(ModelForm):  # Important: Inherit from ModelForm
#     class Meta:
#         model = Property
#         fields = '__all__'


# class ForeclosureResource(resources.ModelResource):
#     class Meta:
#         model = Foreclosure
#         skip_unchanged = True
#         report_skipped = True
#         import_id_fields = ['id']
#         fields = ('id','state','county','case_number','case_number_ext','court_name','case_type','case_status','sale_date','sale_type','sale_status','fcl_final_judgment','sale_price','possible_surplus','verified_surplus','surplus_status','comment')

#     def before_import_row(self, row, **kwargs):
#         required_fields = ['id','state','county','case_number','court_name','case_type','case_status','sale_date','sale_type','sale_status','fcl_final_judgment','sale_price','possible_surplus','verified_surplus','surplus_status','comment']
#         for field in required_fields:
#             if not row.get(field):
#                 raise ValueError(f"Missing required field: {field}")

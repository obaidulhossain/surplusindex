# from django.db.models import Q
# from propertydata.models import *
# def get_filtered_foreclosure_queryset(params):
#     qs = Foreclosure.objects.all()

#     filters = {}

#     selectedState = params.get('stateFilter', '')
#     selectedCounty = params.get('countyFilter', '')
#     selectedSaletype = params.get('saletypeFilter', '')
#     published = params.get('published', '')

#     saleFROM = params.get('sale_from', '')
#     saleTO = params.get('sale_to', '')
#     saledateYear = params.get('sale_date_year', '')
#     saledateMonth = params.get('sale_date_month', '')

#     if selectedState:
#         filters["state__iexact"] = selectedState
#     if selectedCounty:
#         filters["county__iexact"] = selectedCounty
#     if selectedSaletype:
#         filters["sale_type__iexact"] = selectedSaletype

#     if published.lower() == "true":
#         filters["published"] = True
#     elif published.lower() == "false":
#         filters["published"] = False

#     if saleFROM:
#         filters["sale_date__gte"] = saleFROM
#     if saleTO:
#         filters["sale_date__lte"] = saleTO
#     if saledateYear.isdigit():
#         filters["sale_date__year"] = int(saledateYear)
#     if saledateMonth.isdigit():
#         filters["sale_date__month"] = int(saledateMonth)

#     qs = qs.filter(**filters)

#     # ---- Surplus status ----
#     surplus_filters = [
#         params.get(k) for k in [
#             'status_nd','status_ps','status_nps',
#             'status_fa','status_mf','status_fc','status_ns'
#         ] if params.get(k)
#     ]
#     if surplus_filters:
#         qs = qs.filter(surplus_status__in=surplus_filters)

#     # ---- Sale status ----
#     sale_filters = [
#         params.get(k) for k in [
#             'sale_status_active','sale_status_sold',
#             'sale_status_unsold','sale_status_soldtoplaintiff',
#             'sale_status_bankruptcy','sale_status_canceled'
#         ] if params.get(k)
#     ]
#     if sale_filters:
#         qs = qs.filter(sale_status__in=sale_filters)

#     return qs
from propertydata.models import *
def get_filtered_foreclosure_queryset(params):

    selectedState = params.get('stateFilter', '')
    selectedCounty = params.get('countyFilter', '')
    selectedSaletype = params.get('saletypeFilter', '')
    published = params.get('published','')

    surplusStatusND = params.get('status_nd', '')
    surplusStatusPS = params.get('status_ps', '')
    surplusStatusNPS = params.get('status_nps', '')
    surplusStatusFA = params.get('status_fa', '')
    surplusStatusMF = params.get('status_mf', '')
    surplusStatusFC = params.get('status_fc', '')
    surplusStatusNS = params.get('status_ns', '')
    saleStatusACTIVE = params.get('sale_status_active', '')
    saleStatusSOLD = params.get('sale_status_sold', '')
    saleStatusUNSOLD = params.get('sale_status_unsold', '')
    saleStatusSOLDTOPLT = params.get('sale_status_soldtoplaintiff', '')
    saleStatusBANKRUPTCY = params.get('sale_status_bankruptcy', '')
    saleStatusCANCELED = params.get('sale_status_canceled', '')

    saleFROM = params.get('sale_from','')
    saleTO = params.get('sale_to','')
    
    saledateYear = params.get('sale_date_year', '')
    if saledateYear.isdigit():
        saledateYear = int(saledateYear)
    
    saledateMonth = params.get('sale_date_month', '')
    if saledateMonth.isdigit():
        saledateMonth = int(saledateMonth)


# -------------Base querysets----------------------------
    leads_queryset = (
        Foreclosure.objects.all()
        )
    # -------------Filters-----------------------------------
    filters = {}
    if selectedState:
        filters["state__iexact"] = selectedState
    if selectedCounty:
        filters["county__iexact"] = selectedCounty
    if selectedSaletype:
        filters["sale_type__iexact"] = selectedSaletype
    if published.lower() == "true":
        filters["published"] = True
    elif published.lower() == "false":
        filters["published"] = False
    if saleFROM:
        filters["sale_date__gte"] = saleFROM
    if saleTO:
        filters["sale_date__lte"] = saleTO
    if saledateYear:
        filters["sale_date__year"] = saledateYear
    if saledateMonth:
        filters["sale_date__month"] = saledateMonth
 
    leads_queryset = leads_queryset.filter(**filters)

# --------------- Surplus Status --------------------------------------------------
    surplus_filters = []
    if surplusStatusND:
        surplus_filters.append(surplusStatusND)
    if surplusStatusPS:
        surplus_filters.append(surplusStatusPS)
    if surplusStatusNPS:
        surplus_filters.append(surplusStatusNPS)
    if surplusStatusFA:
        surplus_filters.append(surplusStatusFA)
    if surplusStatusMF:
        surplus_filters.append(surplusStatusMF)
    if surplusStatusFC:
        surplus_filters.append(surplusStatusFC)
    if surplusStatusNS:
        surplus_filters.append(surplusStatusNS)

    if surplus_filters:
        leads_queryset = leads_queryset.filter(surplus_status__in=surplus_filters)
    #-------------------------------------------------------------------------------

# ----------------- Sale Status -------------------------------------------------
    sale_filters = []
    if saleStatusACTIVE:
        sale_filters.append(saleStatusACTIVE)
    if saleStatusSOLD:
        sale_filters.append(saleStatusSOLD)
    if saleStatusCANCELED:
        sale_filters.append(saleStatusCANCELED)
    if saleStatusUNSOLD:
        sale_filters.append(saleStatusUNSOLD)
    if saleStatusSOLDTOPLT:
        sale_filters.append(saleStatusSOLDTOPLT)
    if saleStatusBANKRUPTCY:
        sale_filters.append(saleStatusBANKRUPTCY)

    if sale_filters:
        leads_queryset = leads_queryset.filter(sale_status__in=sale_filters)
    
    qs = leads_queryset

    return qs
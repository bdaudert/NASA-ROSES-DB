import operator

from config import statics

def check_form():
    pass

def set_form_options(variables):
    form_options = {}
    for var_key, dflt in variables.iteritems():
        if var_key in statics['form_option_keys']:
            # form_options[var_key] = statics['all_' + var_key]
            fo = statics['all_' + var_key]
            if isinstance(fo, dict):
                # Sort by dict values
                sorted_fo = dict(sorted(fo.items(), key=operator.itemgetter(1)))
                form_options[var_key] = sorted_fo
            else:
                form_options[var_key] = fo

    # Override default form options if needed
    var = variables['variable']
    region = variables['region']
    dataset = variables['dataset']
    # Set the year form options
    s_year = int(statics['all_years'][dataset][0])
    e_year = int(statics['all_years'][dataset][1])
    form_options['year'] = [str(year) for year in range(s_year, e_year + 1)]

    # Set datasets
    form_ds = {}
    for ds in statics['dataset_by_var'][var]:
        form_ds[ds] = statics['all_dataset'][ds]
    form_options['dataset'] = form_ds

    # Set the features
    # FIX ME: we need to set the features according to variable options
    form_options['features'] = statics['all_features']

    return form_options

def set_template_values(req_args, app_name, method):
    '''
    Args:
    req_args: flask.request.args object
    app_name: application name, e.g. OpenET-1
    dOn: default or not; if dOn =  default
    method: HTTP method GET, POST or shareLink
    Returns:
    tv: a dictionary of template variables
    '''

    tv = {
        'app_name': app_name,
        'variables': statics['variable_defaults'],
        'form_options': {}
    }
    # Overrode default variables if not GET
    if method == 'POST' or (method == "GET" and req_args):
        for var_key, dflt in tv['variables'].iteritems():
            if isinstance(dflt, list):
                # LAME: can't enter default list as with get
                form_val = req_args.getlist(var_key)
                if not form_val:
                    form_val = dflt
            else:
                form_val = req_args.get(var_key, dflt)
            tv['variables'][var_key] = form_val

    # Set form options
    tv['form_options'] = set_form_options(tv['variables'])
    return tv
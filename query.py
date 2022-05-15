import re
import yaml, datetime, webbrowser
from lib.common.db import Db
from lib.common.profitability import Profitability
from lib.common.exchange_rate_source import ExchangeRateSource
import dearpygui.dearpygui as dpg


def load_conf(conf_name: str):
    return yaml.safe_load(open(conf_name, 'r'))

def save_conf(conf_name: str, data: dict):
    yaml.safe_dump(data, open(conf_name,'w'))

conf = load_conf('config/scraper.yml')

def dprint(*args):
    print(f'{datetime.datetime.now()}', *args)

# def get_item_serialnumber(item: str) -> str:
#     m = re.search(r'\(([a-zA-Z0-9\- /\\\.]+)\)', item)
#     return m[1] if m else item

def get_item_legend_key(retailer: str, item: str) -> str:
    return f'{retailer}_{item}'

def main():

    db = Db()
    
    last_snapshot_id = db.get_latest_snapshot_id()

    exchange_rate_source = ExchangeRateSource()
    profitability = Profitability()

    map_query_serialnumberpricesnapshots = {}

    def cb_listbox_queries(sender, app_data):
        buckets = map_query_serialnumberpricesnapshots[app_data]
        plot_user_data = dpg.get_item_user_data('plot_price_dynamics')
        # remove existing series
        for s in plot_user_data['series']:
            dpg.delete_item(s)
        plot_user_data['series'] = []

        for serialnumber in sorted(buckets.keys()):
            itemlist = buckets[serialnumber]

            is_bucket_recent = any([x.snapshot_id == last_snapshot_id for x in itemlist])

            # skip any buckets that are not included in last snapshot
            if is_bucket_recent:
                data_x = [item.timestamp for item in itemlist]
                data_x = [datetime.datetime.fromisoformat(x).timestamp() for x in data_x]

                data_y = [item.price for item in itemlist]
                plot_user_data['series'].append( dpg.add_line_series(x=data_x, y=data_y, label=serialnumber, parent='y_axis') )

        dpg.fit_axis_data('x_axis')
        dpg.fit_axis_data('y_axis')


    def cb_go(sender, app_data, user_data):
        webbrowser.open(user_data)

    def cb_sort(sender, sort_specs):

        # sort_specs scenarios:
        #   1. no sorting -> sort_specs == None
        #   2. single sorting -> sort_specs == [[column_id, direction]]
        #   3. multi sorting -> sort_specs == [[column_id, direction], [column_id, direction], ...]
        #
        # notes:
        #   1. direction is ascending if == 1
        #   2. direction is ascending if == -1

        # no sorting case
        if sort_specs is None: return

        columns = dpg.get_item_children(sender, 0)
        column_pos = columns.index(sort_specs[0][0])

        rows = dpg.get_item_children(sender, 1)

        # create a list that can be sorted based on column_pos value, keeping track of row and value used to sort
        sortable_list = []
        for row in rows:
            cells = dpg.get_item_children(row, 1)
            cell = cells[column_pos]
            value = dpg.get_value(cell)
            if value is None:
                return  # we can't sort this column!
            sortable_list.append([row, value])
    

        def try_float_conv(x):
            try:
                return float(x)
            except:
                return x

        sortable_list.sort(key=lambda e: try_float_conv(e[1]), reverse=sort_specs[0][1] < 0)

        # create list of just sorted row ids
        new_order = [pair[0] for pair in sortable_list]

        dpg.reorder_items(sender, 1, new_order)

    dprint('creating context')
    dpg.create_context()

    # with dpg.font_registry():
    #     default_font = dpg.add_font("SF-Mono-Regular.otf", 14)
    # dpg.bind_font(default_font)

    with dpg.window(tag='main'):

        with dpg.collapsing_header(label='latest price snapshot + roi'):
            with dpg.table(
                    header_row=True,
                    resizable=True,
                    sortable=True,
                    hideable=True,
                    reorderable=True, 
                    scrollX=True,
                    scrollY=True, 
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    row_background=True,
                    policy=dpg.mvTable_SizingFixedFit,
                    callback=cb_sort):

                dpg.add_table_column(label='retailer')
                dpg.add_table_column(label='query')
                dpg.add_table_column(label='item',init_width_or_weight=350)
                dpg.add_table_column(label='price')
                dpg.add_table_column(label='price_usd')
                dpg.add_table_column(label='roi_m', default_sort=True)
                dpg.add_table_column(label='daily_profit_usd')

                with dpg.theme(tag='go_button_theme'):
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 100, 255))
                        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 100, 255, 100))
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 100, 255, 50))
                        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 1, 1)


                for s in conf['search_keywords']:
                    for e in db.get_latest(s):
                        daily_profit_usd = profitability.get_daily_profit_usd(s)
                        monthly_profit_usd = daily_profit_usd * 30
                        roi_months = e.price * exchange_rate_source.get_UAH_USD()  / monthly_profit_usd

                        with dpg.table_row():
                            dpg.add_text(e.retailer)
                            dpg.add_text(e.query)

                            with dpg.group(horizontal=True):
                                dpg.add_button(label='go',user_data=e.url, callback=cb_go)
                                dpg.bind_item_theme(dpg.last_item(), 'go_button_theme')
                                dpg.add_text(e.title)
                            
                            dpg.add_text(e.price)
                            dpg.add_text(round(e.price *  exchange_rate_source.get_UAH_USD()) )
                            dpg.add_text(round(roi_months,1))
                            dpg.add_text(round(daily_profit_usd,2))

    
        with dpg.collapsing_header(label='price dynamics'):

            queries = [ query for query in db.get_distinct_queries() ]
            for q in queries:
                items_for_query = db.get_items(q)
                # group into buckets by item serial number
                buckets = {}
                for x in items_for_query:
                    buckets.setdefault(get_item_legend_key(x.retailer,x.item), []).append(x)
                map_query_serialnumberpricesnapshots[q] = buckets

            with dpg.group(horizontal=True):
                dpg.add_listbox(tag='listbox_queries', width=150, items=queries, callback=cb_listbox_queries, num_items=len(queries))
                with dpg.plot(label='price dynamics', width=-1, height=-1, tag='plot_price_dynamics', user_data=dict(series=[])):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label='date', tag='x_axis', time=True)
                    dpg.add_plot_axis(dpg.mvYAxis, label='price, UAH', tag='y_axis')
                    #dpg.add_scatter_series([], [], parent='y_axis', tag='scatter_price')


    dprint('creating viewport')
    dpg.create_viewport(title='retail price scraper query')#, x_pos=window_geometry_conf['x'],y_pos=window_geometry_conf['y'],width=window_geometry_conf['w'],height=window_geometry_conf['h'])
    dpg.set_primary_window('main',True)
    
    dprint('setting up dpg')
    dpg.setup_dearpygui()

    dprint('displaying viewport')
    dpg.show_viewport()
    
    dprint('resizing viewport')
    window_geometry_conf = load_conf('config/window.yml')
    dpg.set_viewport_pos([window_geometry_conf['x'],window_geometry_conf['y']])
    dpg.set_viewport_width(window_geometry_conf['w'])
    dpg.set_viewport_height(window_geometry_conf['h'])
    

    dprint('running dpg event loop')
    dpg.start_dearpygui()

    #save viewport
    window_geometry_conf = dict(x=dpg.get_viewport_pos()[0],y=dpg.get_viewport_pos()[1],w=dpg.get_viewport_width(),h=dpg.get_viewport_height())
    save_conf('config/window.yml', window_geometry_conf)
    
    dprint('shutting down')
    dpg.destroy_context()    


if __name__ == '__main__':
    main()

def calc_page_num(current_page, total_page):
    """
    Default the max page shown being 9.
    :param current_page: current page number
    :param total_page: total page number
    :return: the page number to show in pagination
    """
    if total_page <= 7:
        start_page, end_page = 1, total_page
    elif current_page - 3 < 1:
        start_page, end_page = 1, 7
    elif current_page + 3 > total_page:
        start_page, end_page = total_page - 6, total_page
    else:
        start_page, end_page = current_page - 3, current_page + 3

    return start_page, end_page

import math

RETRIEVABILITY_POINTS_DOCUMENT_ENTRY = {'1': [20.0, 10], '50': [19.6, 10], '100': [19.1, 10], '500': [17.1, 20],
                                        '1000': [14.6, 20], '1500': [12.1, 20], '2000': [9.6, 20], '2500': [8.6, 50],
                                        '3000': [7.6, 50], '3500': [6.6, 50], '4000': [5.6, 50], '4500': [4.6, 50],
                                        '5000': [3.6, 100], '5500': [3.1, 100], '6000': [2.6, 100], '6500': [2.1, 100],
                                        '7000': [1.6, 100]}
MAX_SEARCH_RESULTS = 8000


def compute_points(entry_counter, related_documents_counter, average_related_doc_position, query, original_query):
    """
    Computes the different kinds of points for the query entered by the user
    @param entry_counter: Position of the document in demand
    @type entry_counter: Integer
    @param related_documents_counter: Number of related documents found in the search parameter
    @type related_documents_counter: Integer
    @param average_related_doc_position: The average position of the related documents inside
            the search parameter
    @type average_related_doc_position: Integer
    @param query: The search query the user entered
    @type query: String
    @param original_query: The original query belonging to the document in demand
    @type original_query: String
    @return: Tuple of all the different kind of points
    @rtype: Tuple
    """

    document_pos_points = points_document_pos(entry_counter)
    document_pos_points = int(document_pos_points)
    num_related_docs_points = points_number_related_documents(related_documents_counter)
    avg_pos_related_docs_points = points_average_pos_related_documents(related_documents_counter,
                                                                       average_related_doc_position)
    query_length_points = points_query_length(query, original_query)
    total_points = document_pos_points + num_related_docs_points + avg_pos_related_docs_points + query_length_points
    return document_pos_points, num_related_docs_points, avg_pos_related_docs_points, query_length_points, total_points


def points_document_pos(entry_counter):
    """
    This function computes the points for the position of the document in demand
    @param entry_counter: The position of the document
    @type entry_counter: Integer
    @return: The computet points
    @rtype: Integer
    """
    points = 0
    # First check if entry_counter is larger than 7000, if so then points is a fixed value
    if entry_counter > 7000:
        points = 1.0
        return points
    else:
        # determine bounds
        for key in RETRIEVABILITY_POINTS_DOCUMENT_ENTRY:
            if entry_counter == int(key):
                points = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[key][0]
                return points

            if entry_counter > int(key):
                lower_bound = key

            if entry_counter < int(key):
                upper_bound = key
                break

        # Now determine if entry_counter is nearer the upper or the lower bound
        difference_lower_bound = entry_counter - int(lower_bound)
        difference_upper_bound = int(upper_bound) - entry_counter
        step_size = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[upper_bound][1]

        if difference_lower_bound <= difference_upper_bound:
            step = int(lower_bound)
            points = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[lower_bound][0]

        if difference_lower_bound > difference_upper_bound:
            step = int(upper_bound)
            points = RETRIEVABILITY_POINTS_DOCUMENT_ENTRY[upper_bound][0]

        # compute the actual value of the range in which the pos of the document lies
        while step < entry_counter:
            if difference_lower_bound <= difference_upper_bound:
                points = points - 0.1
                points = round(points, 1)
                step = step + step_size

            if difference_lower_bound > difference_upper_bound:
                points = points + 0.1
                step = step - step_size

    return 10 * points


def points_number_related_documents(related_documents_counter):
    """
    This function computes the points for the number of related documents retrieved
    with the query of the user.
    @param related_documents_counter: Number of found related documents
    @type related_documents_counter: Integer
    @return: Computed points
    @rtype: Integer
    """
    if related_documents_counter > 149:
        return 150
    else:
        return related_documents_counter


def points_average_pos_related_documents(related_documents_counter, average_related_doc_position):
    """
    This function computes the points for the average position of the related documents.
    @param related_documents_counter: Number of related documents
    @type related_documents_counter: Integer
    @param average_related_doc_position: Average positio of the related documents
    @type average_related_doc_position: Integer
    @return: Computet points
    @rtype: Integer
    """
    if related_documents_counter == 0:
        return 0

    average_related_doc_position = normal_round(average_related_doc_position/related_documents_counter)
    points = 100
    for i in range(160, MAX_SEARCH_RESULTS, 160):
        if average_related_doc_position <= i:
            return points
        else:
            points = points - 2
    return points


def points_query_length(query, original_query):
    """
    Computes the points for the length of the query submittet by the user
    @param query: Query submitted by the user
    @type query: String
    @param original_query: Original query that belongs to the document in demand
    @type original_query: String
    @return: Computed points
    @rtype: Integer
    """
    query_length = len(query.split())
    original_query_length = len(original_query.split())

    if query_length < original_query_length or query_length == original_query_length:
        return 50

    else:
        length_difference = query_length - original_query_length
        return 50 - length_difference


def normal_round(n):
    """
    Rounds numbers according to the common rounding rules.
    @param n: Number that should be rounded
    @type n: Float
    @return: Rounded number
    @rtype: Integer
    """
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)

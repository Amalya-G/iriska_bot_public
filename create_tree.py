from treelib import Tree, Node


# избыточность if. дубли одинаковой логики вынести в методы
def create_tree(worksheet):
    # Строим дерево из данных
    offer_count = len(worksheet.row_values(1))+1 #worksheet.spreadsheet.sheet1.col_count
    contents = worksheet.col_values(1)
    tree = Tree()
    root_node = tree.create_node("root", identifier="root")
    for i in range(2, offer_count):
        data_column = worksheet.col_values(i)
        industry_id = f"{root_node.identifier}_{data_column[0]}"
        industry_node = tree.get_node(industry_id) # когда индустрия есть, но не по порядку
        if tree.contains(industry_id) == False:  # Индустрия
            industry_node = tree.create_node(data_column[0], industry_id, root_node, data_column[0])
            direction_id = f"{industry_node.identifier}_{data_column[1]}"
            if tree.contains(direction_id) == False:  # Направление
                direction_node = tree.create_node(data_column[1], direction_id, industry_node,
                                                  data_column[1])
                cases_id = f"{direction_id}_{data_column[2]}"
                if tree.contains(cases_id) == False:  # Кейсы
                    cases_node = tree.create_node(data_column[2], cases_id, direction_node, data_column[2])
                    for i in range(3, 9):
                        info_id = f"{cases_id}_{contents[i]}"
                        tree.create_node(contents[i], info_id, cases_node, data_column[i])
            else:
                cases_id = f"{direction_id}_{data_column[2]}"
                direction_node = tree.get_node(direction_id)
                if tree.contains(cases_id) == False:  # Кейсы
                    cases_node = tree.create_node(data_column[2], cases_id, direction_node, data_column[2])
                    for i in range(3, 9):
                        info_id = f"{cases_id}_{contents[i]}"
                        tree.create_node(contents[i], info_id, cases_node, data_column[i])
        else:
            direction_id = f"{industry_id}_{data_column[1]}"
            industry_node = tree.get_node(industry_id)
            if tree.contains(direction_id) == False:  # Направление
                direction_node = tree.create_node(data_column[1], direction_id, industry_node,
                                                  data_column[1])
                cases_id = f"{direction_id}_{data_column[2]}"
                if tree.contains(cases_id) == False:  # Кейсы
                    cases_node = tree.create_node(data_column[2], cases_id, direction_node, data_column[2])
                    for i in range(3, 9):
                        info_id = f"{cases_id}_{contents[i]}"
                        tree.create_node(contents[i], info_id, cases_node, data_column[i])
            else:
                cases_id = f"{direction_id}_{data_column[2]}"
                direction_node = tree.get_node(direction_id)
                if tree.contains(cases_id) == False:  # Кейсы
                    cases_node = tree.create_node(data_column[2], cases_id, direction_node, data_column[2])
                    for i in range(3, 9):
                        info_id = f"{cases_id}_{contents[i]}"
                        tree.create_node(contents[i], info_id, cases_node, data_column[i])
    print('Дерево создано!')
    tree.show()
    return tree
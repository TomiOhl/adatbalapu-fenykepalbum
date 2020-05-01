# telepulesek fancy listaban
from db_actions import exec_return


def get_settlements():
    # lenyilo listahoz telepulesek listaja
    settlements_query = exec_return("""SELECT Settlements.Id, Settlements.Name, Countries.Name\
                                        FROM Settlements, Countries\
                                        WHERE Settlements.Country = Countries.Id ORDER BY Country, Settlements.Name""")[
        1]
    # atcsinaljuk ugy, hogy az orszagok is kapjanak opciot, elvalasztaskent
    settlements = []
    curr_country = ""
    for item in settlements_query:
        if item[2] != curr_country:
            curr_country = item[2]
            settlements.append(tuple(["x", f"*****{curr_country}*****"]))
        settlements.append(tuple([item[0], item[1]]))
    return settlements

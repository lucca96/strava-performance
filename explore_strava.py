import json

from src.client import ApiBudgetExceeded, StravaClient
from src.extract import get_all_activities


def print_activity_summary(activities):
    print("\n=== LISTA DE ATIVIDADES ===\n")

    for activity in activities:
        print(f"ID: {activity['id']}")
        print(f"Nome: {activity['name']}")
        print(f"Tipo: {activity['type']}")
        print(f"Data: {activity['start_date_local']}")
        print(f"HR?: {activity.get('has_heartrate')}")
        print(f"Device: {activity.get('device_name')}")
        print("-" * 40)


def explore_activity(activity_id, client):
    print(f"\nExplorando atividade {activity_id}\n")
    details = client.get_activity_details(activity_id)

    print("\n=== DETALHES COMPLETOS ===\n")
    print(json.dumps(details, indent=2, ensure_ascii=False)[:2000])

    print("\n=== CAMPOS INTERESSANTES ===\n")
    print("Suffer Score:", details.get("suffer_score"))
    print("Average HR:", details.get("average_heartrate"))
    print("Max HR:", details.get("max_heartrate"))
    print("Average Cadence:", details.get("average_cadence"))
    print("Device:", details.get("device_name"))
    print("Perceived Exertion:", details.get("perceived_exertion"))

    streams = client.get_activity_streams(activity_id)
    if not streams:
        print("\nSem streams disponiveis")
        return

    print("\n=== STREAMS DISPONIVEIS ===\n")
    for key in streams.keys():
        print("-", key)

    print("\n=== AMOSTRA DE DADOS ===\n")
    for key in streams.keys():
        data = streams[key]["data"]
        print(f"{key}: {data[:5]}")


def main():
    client = StravaClient()
    activities = get_all_activities(max_pages=1, client=client)

    print("\nEscolha uma opcao:")
    print("1 - Listar atividades cache/API page 1")
    print("2 - Explorar por ID")
    print("3 - Explorar primeira com HR da page 1")

    option = input("\nOpcao: ")

    try:
        if option == "1":
            print_activity_summary(activities)
        elif option == "2":
            activity_id = input("Digite o ID da atividade: ")
            explore_activity(activity_id, client)
        elif option == "3":
            activities_with_hr = [a for a in activities if a.get("has_heartrate")]
            if not activities_with_hr:
                print("Nenhuma atividade com HR encontrada na page 1")
                return
            explore_activity(activities_with_hr[0]["id"], client)
        else:
            print("Opcao invalida")
    except ApiBudgetExceeded as exc:
        print(f"Orcamento de API atingido: {exc}")

    print(f"\nChamadas API usadas: {client.calls_made}/{client.max_calls}")
    print(f"Cache hits: {client.cache_hits}")


if __name__ == "__main__":
    main()

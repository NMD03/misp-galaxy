from generator import Galaxy
import json
import os
import time

CLUSTER_PATH = "../../clusters"
SITE_PATH = "./site/docs"
FILES_TO_IGNORE = []


if __name__ == "__main__":
    start_time = time.time()
    galaxies_fnames = []
    for f in os.listdir(CLUSTER_PATH):
        if ".json" in f and f not in FILES_TO_IGNORE:
            galaxies_fnames.append(f)
    galaxies_fnames.sort()


    galaxy_dict = {}
    galaxies = []
    for galaxy in galaxies_fnames:
        with open(os.path.join(CLUSTER_PATH, galaxy)) as fr:
            galaxie_json = json.load(fr)
            galaxies.append(
                Galaxy(
                    galaxie_json["values"],
                    galaxie_json["authors"],
                    galaxie_json["description"],
                    galaxie_json["name"],
                    galaxy.split(".")[0],
                )
            )
            galaxy_dict[galaxie_json["name"]] = galaxies[-1]

    cluster_dict = {}
    for galaxy in galaxies:
        for cluster in galaxy.clusters:
            cluster_dict[cluster.uuid] = cluster

    old_galaxies = [
                    "Enterprise Attack - Attack Pattern", 
                    "Enterprise Attack - Course of Action",
                    "Enterprise Attack - Intrusion Set",
                    "Enterprise Attack - Malware",
                    "Mobile Attack - Attack Pattern",
                    "Mobile Attack - Course of Action",
                    "Mobile Attack - Intrusion Set",
                    "Mobile Attack - Malware",
                    "Pre Attack - Attack Pattern",
                    "Pre Attack - Intrusion Set",
                    "Enterprise Attack - Tool",
                    "Mobile Attack - Tool"
                    ]
    new_galaxies = {
                    "Enterprise Attack - Attack Pattern": "Attack Pattern", 
                    "Enterprise Attack - Course of Action": "Course of Action",
                    "Enterprise Attack - Intrusion Set": "Intrusion Set",
                    "Enterprise Attack - Malware": "Malware",
                    "Mobile Attack - Attack Pattern": "Attack Pattern",
                    "Mobile Attack - Course of Action": "Course of Action",
                    "Mobile Attack - Intrusion Set" : "Intrusion Set",
                    "Mobile Attack - Malware": "Malware",
                    "Pre Attack - Attack Pattern": "Attack Pattern",
                    "Pre Attack - Intrusion Set": "Intrusion Set",
                    "Enterprise Attack - Tool": "mitre-tool",
                    "Mobile Attack - Tool": "mitre-tool"
                    }
    

    not_found_cluster = {}
    relation_diff = {}
    for galaxy in galaxies:
        if galaxy.name in old_galaxies:
            for cluster in galaxy.clusters:
                 
                if cluster.uuid not in [cluster.uuid for cluster in galaxy_dict[new_galaxies[galaxy.name]].clusters]:
                    with open("notFound.txt", "a") as f:
                        f.write(f"Cluster: {cluster.value}")
                        f.write("\n")
                        f.write(f"UUID: {cluster.uuid}")
                        f.write("\n")
                        f.write(f"Old Galaxy: {cluster.galaxie.name}")
                        f.write("\n")
                        f.write(f"UUID not found in new Galaxie: {new_galaxies[galaxy.name]}")
                        f.write("\n")
                        f.write("///////////////////////////////")
                        f.write("\n")
                        f.write("Looking for cluster name in new galaxy")
                        f.write("\n")
                        not_found_cluster[cluster.uuid] = cluster.galaxie.name
                        found = False
                        for new_cluster in galaxy_dict[new_galaxies[galaxy.name]].clusters:
                            if cluster.value == new_cluster.value:
                                f.write(f"Cluster found in new galaxy: {new_galaxies[galaxy.name]}")
                                f.write("\n")
                                f.write(f"UUID: {new_cluster.uuid}")
                                f.write("\n")
                                f.write("###############")
                                f.write("\n")
                                f.write("Compare clusters")
                                f.write("\n")
                                if cluster.description != new_cluster.description:
                                    f.write(f"Description not equal: {cluster.description} != {new_cluster.description}")
                                    f.write("\n")
                                if cluster.related_list != new_cluster.related_list:
                                    f.write(f"Related list not equal: {cluster.related_list} != {new_cluster.related_list}")
                                    f.write("\n")
                                if cluster.meta != new_cluster.meta:
                                    f.write(f"Meta not equal: {cluster.meta} != {new_cluster.meta}")
                                    f.write("\n")
                                if cluster.date != new_cluster.date:
                                    f.write(f"Date not equal: {cluster.date} != {new_cluster.date}")
                                    f.write("\n")
                                found = True
                        if not found:
                            f.write("Cluster not found in new galaxy")
                            f.write("\n")
                        f.write("--------------------------------------------------------")
                        f.write("\n")
                else:
                    old_relations = []
                    new_relations = []
                    if cluster.related_list is not None:
                        old_relations = [relation for relation in cluster.related_list]
                    for new_cluster in galaxy_dict[new_galaxies[galaxy.name]].clusters:
                        if new_cluster.uuid == cluster.uuid:
                            if new_cluster.related_list is not None:
                                new_relations = [relation for relation in new_cluster.related_list]
                    if old_relations != new_relations:
                        for relation in old_relations:
                            if relation not in new_relations:
                                with open("relations.txt", "a") as f:
                                    relation_diff[str(relation)] = cluster.uuid
                                    f.write(f"Cluster: {cluster.value}")
                                    f.write("\n")
                                    f.write(f"UUID: {cluster.uuid}")
                                    f.write("\n")
                                    f.write(f"Old Galaxy: {cluster.galaxie.name}")
                                    f.write("\n")
                                    f.write(f"Relation not found in new Galaxie: {new_galaxies[galaxy.name]}")
                                    f.write("\n")
                                    f.write(f"Relation: {relation}")
                                    f.write("\n")
                                    if relation["dest-uuid"] in cluster_dict:
                                        f.write(f"Related Cluster: {cluster_dict[relation['dest-uuid']].value}, Galaxy: {cluster_dict[relation['dest-uuid']].galaxie.name}")
                                    else:
                                        f.write(f"Related Cluster: Private Cluster")
                                    f.write("\n")
                                    f.write("///////////////////////////////")
                                    f.write("\n")
                                    f.write("Is Relation to old galaxy?")
                                    if relation['dest-uuid'] in cluster_dict:
                                        if cluster_dict[relation['dest-uuid']].galaxie.name in old_galaxies:
                                            f.write(" Yes")
                                            f.write("\n")
                                            f.write(f"Is Cluster '{cluster_dict[relation['dest-uuid']].value}' in new galaxy?")
                                            if cluster_dict[relation['dest-uuid']].uuid in not_found_cluster.keys():
                                                f.write(" No")
                                                f.write("\n")
                                            else:
                                                f.write(" Yes --> relation from new galaxy cluster to new galaxy cluster should be created")
                                                f.write("\n")

                                        else:
                                            f.write(" No --> Why is this relation not in new galaxy?")
                                            f.write("\n")
                                    f.write("--------------------------------------------------------")
                                    f.write("\n")

    print(f"Finished evaluation in {time.time() - start_time} seconds")
    print(f"{len(not_found_cluster)} clusters not found in new galaxies")
    print(f"{len(relation_diff)} relations not found in new galaxies")
    print("Check notFound.txt and relations.txt for more information")
from generator import Galaxy
import json
import os
import time

CLUSTER_PATH = "../../clusters"
SITE_PATH = "./site/docs"
FILES_TO_IGNORE = []
WRITE_FILES = True
ENRICH_NEW_GALAXIES = True

def get_lost_clusters(galaxies, old_galaxies, new_galaxies, galaxy_dict):
    not_found_cluster = {}
    for galaxy in galaxies:
        if galaxy.name in old_galaxies:
            for cluster in galaxy.clusters:
                if cluster.uuid not in [cluster.uuid for cluster in galaxy_dict[new_galaxies[galaxy.name]].clusters]:
                    not_found_cluster[cluster.uuid] = cluster.galaxie.name
                    if WRITE_FILES:
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
    return not_found_cluster

def get_relation_diff(galaxies, old_galaxies, new_galaxies, galaxy_dict, cluster_dict):
    relation_diff = {}
    for galaxy in galaxies:
        if galaxy.name in old_galaxies:
            for cluster in galaxy.clusters:
                if cluster.uuid in [cluster.uuid for cluster in galaxy_dict[new_galaxies[galaxy.name]].clusters]:
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
                                relation_diff[str(relation)] = cluster.uuid
                                if WRITE_FILES:
                                    with open("relations.txt", "a") as f:
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
                                        f.write("--------------------------------------------------------")
                                        f.write("\n")
    return relation_diff

def enrich_new_galaxies(galaxy_map, cluster_dict, not_found_cluster):
    new_galaxie_json = {}
    for old_galaxy, new_galaxy in galaxy_map.items():
        with open(os.path.join(CLUSTER_PATH, f"{new_galaxy.json_file_name}.json")) as fr:
            new_galaxie_json[new_galaxy] = json.load(fr)
        for cluster in old_galaxy.clusters:
            if cluster.uuid in not_found_cluster: # Cluster not found in new galaxy
                continue
            if cluster.uuid in cluster_dict and cluster.related_list is not None: # Cluster is exists in new galaxy and has relations
                for relation in cluster.related_list:
                    if relation["dest-uuid"] in not_found_cluster: # Related cluster not found in new galaxy
                        continue
                    if relation not in [relation for relation in [cluster.related_list for cluster in new_galaxy.clusters]]:
                        for entry in new_galaxie_json[new_galaxy]["values"]:
                            if entry["uuid"] == cluster.uuid:
                                entry["related"].append(relation)
                                break
        with open(os.path.join(CLUSTER_PATH, f"{new_galaxy.json_file_name}.json"), "w") as fw:
            json.dump(new_galaxie_json[new_galaxy], fw, indent=2)

def map_galaxies(galaxies, galaxy_dict):
    galaxy_map = {}
    for old_galaxy, new_galaxy in galaxies.items():
        galaxy_map[galaxy_dict[old_galaxy]] = galaxy_dict[new_galaxy]

    return galaxy_map


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
    

    not_found_cluster = get_lost_clusters(galaxies, old_galaxies, new_galaxies, galaxy_dict)
    relation_diff = get_relation_diff(galaxies, old_galaxies, new_galaxies, galaxy_dict, cluster_dict)
    print(f"{len(not_found_cluster)} clusters not found in new galaxies")
    print(f"{len(relation_diff)} relations not found in new galaxies")
    print("Check notFound.txt and relations.txt for more information")

    if ENRICH_NEW_GALAXIES:
        galaxy_map = map_galaxies(new_galaxies, galaxy_dict)
        enrich_new_galaxies(galaxy_map, cluster_dict, not_found_cluster)
        print("Enriched new galaxies with missing relations")

    print(f"Finished evaluation in {time.time() - start_time} seconds")
import json
import sys
from .global_methods import *


class ReputationDB:
    individual_reputations: dict
    out_of_date_reputations: dict
    reputations_count: int
    
    def __init__(self, f_saved) -> None:
        self.individual_reputations = dict()
        self.out_of_date_reputations = dict()
        self.reputations_count = 0

        # add for public
        self.f_saved = f_saved

        print(f"INIT ReputationDB: {f_saved}")

        if check_if_file_exists(f"{f_saved}/reputation_database.json"):
            print("GNS FUNCTION: <ReputationDB__init__>")

            individual_reputations_load = json.load(
                open(f"{f_saved}/reputation_database.json")
            )
            self.reputations_count = len(individual_reputations_load)
            self.individual_reputations = individual_reputations_load
        else:
            with open(f"{f_saved}/reputation_database.json", "w") as f:
                json.dump({}, f)

        if check_if_file_exists(f"{f_saved}/out_of_date_reputation_database.json"):
            print("GNS FUNCTION: <out_of_date_ReputationDB__init__>")

            out_of_date_reputations = json.load(
                open(f"{f_saved}/out_of_date_reputation_database.json")
            )
            self.out_of_date_reputations = out_of_date_reputations
        else:
            with open(f"{f_saved}/out_of_date_reputation_database.json", "w") as f:
                json.dump({}, f)

    def save(self, reputation_folder):
        with open(reputation_folder + "/reputation_database.json", "w") as f:
            json.dump(self.individual_reputations, f, indent=4)

        with open(
            reputation_folder + "/out_of_date_reputation_database.json", "w"
        ) as f:
            json.dump(self.out_of_date_reputations, f, indent=4)

    def get_targets_individual_reputation(self, target_index, role):
        target_reputation = dict()
        for key, reputation in self.individual_reputations.items():
            if role.lower() in key.lower():
                if (
                    target_index == reputation["ID"]
                    or target_index == reputation["name"]
                ):
                    target_reputation[key] = reputation
        return target_reputation

    # add public
    def get_publicreputation(self, role):
        individual_publicreputations_load = json.load(
                open(f"{self.f_saved}/public_reputation.json")
            )
        individual_publicreputation = individual_publicreputations_load.get(role, {}) 
        return individual_publicreputation



    def update_individual_reputation(self, reputation, curr_step, reason):
        print("UPDATING INDIVIDUAL REPUTATION")
        for key in reputation.keys():
            if key in self.individual_reputations.keys():
                pre_reputation = self.individual_reputations[key]
                pre_reputation["reason"] = reason
                self.out_of_date_reputations[key + f"_pre_{curr_step}"] = pre_reputation
                self.individual_reputations[key] = reputation[key]
            else:
                self.individual_reputations[key] = reputation[key]
                self.reputations_count += 1

    def get_all_reputations(self, role, self_id, with_self=False):
        all_reputations = dict()
        if role.lower() == "investor":
            input = "Investor"
        elif role.lower() == "trustee":
            input = "Trustee"
        elif role.lower() == "resident":
            input = "Resident"
        elif role.lower() == "player":
            input = "Player"
        for key, reputation in self.individual_reputations.items():
            if with_self and input in key:
                all_reputations[key] = reputation
                continue
            # get all reputation except self reputation
            if f"{input}_{self_id}" != key and input in key:
                all_reputations[key] = reputation
        return all_reputations





import datetime
import json
import sys
from .global_methods import *

sys.path.append("../")


def check_if_gossip_sign_up(persona):
    if (
        persona.scratch.gossip_chat
        and persona.scratch.curr_complain_info["after_sign_up"]
    ):
        return True
    return False


class GossipDB:
    gossips: list
    gossips_count: int
    gossips_incredible_count: int

    def __init__(self, f_saved) -> None:
        self.gossips = []
        self.gossips_count = 0
        self.gossips_incredible_count = 0
        print(f"INIT GossipDB: {f_saved}")

        if check_if_file_exists(f"{f_saved}/gossip_database.json"):
            print("GNS FUNCTION: <GossipDB__init__>")

            gossips_load = json.load(open(f"{f_saved}/gossip_database.json"))
            self.gossips_count = len(gossips_load)
            self.gossips = gossips_load

            for gossip in self.gossips:
                if gossip["credibility level"] in ["very uncredible", "uncredible"]:
                    self.gossips_incredible_count += 1

        else:
            print(
                f"INIT GossipDB: {f_saved}/gossip_database.json could not find")

    def save(self, gossip_folder):
        with open(gossip_folder + "/gossip_database.json", "w") as f:
            json.dump(self.gossips, f, indent=4)

    def add_gossip(self, gossips, curr_step):
        print("GossipDB.add_gossip()")
        for gossip in gossips:
            gossip["created_at"] = curr_step
            self.gossips.append(gossip)
            self.gossips_count += 1
            if gossip["credibility level"] in ["very uncredible", "uncredible"]:
                self.gossips_incredible_count += 1

    def get_target_gossips_info(self, target_persona):
        infos = ""
        weight = ""
        print("GossipDB.get_target_gossips_info()")
        for _, gossip in self.gossips.items():
            # find
            # And only use the gossip that active time is in 30min scope
            active_time = datetime.datetime.strptime(
                gossip["active_time"], "%B %d, %Y, %H:%M:%S"
            )
            if (target_persona.scratch.curr_time - active_time) <= datetime.timedelta(
                minutes=30
            ):
                if gossip["complained ID"] == target_persona.scratch.ID:
                    infos = gossip["gossip info"]
                    weight = gossip["credibility level"]
                    break
        return infos, weight

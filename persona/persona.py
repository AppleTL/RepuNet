from collections import deque
import json
import os
import datetime
from public_reputation.SharedPublicReputationDB import publicreputationDB
from .memory_structures.scratch import Scratch
from reputation.PersonalMemoryDB_Gossip import ReputationDB, GossipDB
from .memory_structures.associative_memory import AssociativeMemory

class Persona:
    name: str
    scratch: Scratch
    reputationDB: ReputationDB
    gossipDB: GossipDB
    associativeMemory: AssociativeMemory

    def __init__(self, name, folder_mem_saved=False, with_reputation=False, with_publicreputation=True, investment=None):
        self.name = name

        scratch_saved = f"{folder_mem_saved}/memory/scratch.json"
        self.scratch = Scratch(scratch_saved, investment)

        gossip_saved = f"{folder_mem_saved}/reputation"
        self.gossipDB = GossipDB(gossip_saved)

        self.with_publicreputation = with_publicreputation
        
        if with_reputation:
            reputation_saved = f"{folder_mem_saved}/reputation"
            self.reputationDB = ReputationDB(reputation_saved)        
        else:
            self.reputationDB = None

        associative_memory_saved = f"{folder_mem_saved}/memory/associative_memory"
        self.associativeMemory = AssociativeMemory(associative_memory_saved, do_load=True)
        self.interaction_memory = {"investor": [], "trustee": []}

        

    def save(self, save_folder):
        scratch_folder = f"{save_folder}/memory/scratch.json"
        self.scratch.save(scratch_folder)
        self.associativeMemory.save()
        reputation_folder = f"{save_folder}/reputation"
        if self.reputationDB:
            self.reputationDB.save(reputation_folder)
        self.gossipDB.save(reputation_folder)


    def record_publicreputation_to_local(self, public_save_folder, index, role):
        try:
            target_data = publicreputationDB.get_target_public_reputation(index, role)
            if not target_data: return

            data = {}
            if os.path.exists(public_save_folder) and os.path.getsize(public_save_folder) > 0:
                with open(public_save_folder, "r", encoding="utf-8") as f:
                    data = json.load(f)

            data[role] = target_data 
            os.makedirs(os.path.dirname(public_save_folder), exist_ok=True)
            with open(public_save_folder, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            with open("reputation_debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now()}] Error: {e}\n")


    def get_latest_memory_list(self):
        id_list = list(self.associativeMemory.event_id_to_node.keys())
        sorted_id_list = sorted(id_list, reverse=False)
        memory_list_investor = []
        memory_list_trustee = []
        for id in sorted_id_list:
            # if self.event_id_to_node[id]["description"].split("investor is")[-1].split("trustee is")[0].strip().strip(",")
            ob = self.associativeMemory.event_id_to_node[id]
            if type(ob) is dict:
                des_str = ob["description"]
            else:
                des_str = ob.description

            if "Failed" in des_str:
                if des_str.split("Investor is")[1].split("and")[0].strip() == self.name:
                    memory_list_investor.append(des_str)
                else:
                    memory_list_trustee.append(des_str)
            elif "Success" in des_str:
                if des_str.split("investor is")[1].split("trustee is")[0].strip().strip(",") == self.name:
                    memory_list_investor.append(des_str)
                else:
                    memory_list_trustee.append(des_str)
        if len(memory_list_investor) >= 5:
            memory_list_investor = memory_list_investor[-5:]
        if len(memory_list_trustee) >= 5:
            memory_list_trustee = memory_list_trustee[-5:]
        return memory_list_investor, memory_list_trustee
    

    # .get_latest_memory_list_target()[0] -> init_persona as investor
    # .get_latest_memory_list_target()[1] -> init_persona as trustee
    
    def get_latest_memory_list_target(self, target_name):
        id_list = list(self.associativeMemory.event_id_to_node.keys())
        sorted_id_list = sorted(id_list, reverse=False)
        memory_list_investor = []
        memory_list_trustee = []
        for id in sorted_id_list:
            # if self.event_id_to_node[id]["description"].split("investor is")[-1].split("trustee is")[0].strip().strip(",")
            ob = self.associativeMemory.event_id_to_node[id]
            if type(ob) is dict:
                des_str = ob["description"]
                object = ob["object"]
            else:
                des_str = ob.description
                object = ob.object
            if object == target_name:
                investor_name = ""     
                # Failed investment: investor is AAA, trustee is BBB
                if "investor is" in des_str and "trustee is" in des_str:
                    investor_name = des_str.split("investor is")[1].split("trustee is")[0].strip().strip(",")
                # Failed investment. Investor is AAA and Trustee is BBB.
                elif "Investor is" in des_str and "Trustee is" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and Trustee is")[0].strip().strip(",")
                elif "Investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and")[0].strip().strip(",")
                elif "investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("investor is")[1].split("and")[0].strip().strip(",")
                if investor_name == self.name:
                    # memory_list_investor.append({
                    #     "description": des_str,
                    #     "investor": self.name,
                    #     "trustee": object
                    # })
                    memory_list_investor.append(des_str)
                else:
                    # memory_list_trustee.append({
                    #     "description": des_str,
                    #     "investor": object,
                    #     "trustee": self.name
                    # })   
                    memory_list_trustee.append(des_str)
        if len(memory_list_investor) >= 5:
            memory_list_investor = memory_list_investor[-5:]
        if len(memory_list_trustee) >= 5:
            memory_list_trustee = memory_list_trustee[-5:]
        # print("=== memory_list_investor ===")
        # print(memory_list_investor)
        # print("=== memory_list_trustee ===")
        # print(memory_list_trustee)
        return memory_list_investor, memory_list_trustee

 



    def get_latest_memory_list_3(self):
        id_list = list(self.associativeMemory.event_id_to_node.keys())
        sorted_id_list = sorted(id_list, reverse=False)
        memory_list_investor = []
        memory_list_trustee = []
        for id in sorted_id_list:
            # if self.event_id_to_node[id]["description"].split("investor is")[-1].split("trustee is")[0].strip().strip(",")
            ob = self.associativeMemory.event_id_to_node[id]
            if type(ob) is dict:
                des_str = ob["description"]
            else:
                des_str = ob.description
            if "Failed" in des_str:
                investor_name = ""
                
                # Failed investment: investor is AAA, trustee is BBB
                if "investor is" in des_str and "trustee is" in des_str:
                    investor_name = des_str.split("investor is")[1].split("trustee is")[0].strip().strip(",")
                # Failed investment. Investor is AAA and Trustee is BBB.
                elif "Investor is" in des_str and "Trustee is" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and Trustee is")[0].strip().strip(",")
                elif "Investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and")[0].strip().strip(",")
                elif "investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("investor is")[1].split("and")[0].strip().strip(",")

                if investor_name == self.name:
                    memory_list_investor.append(des_str)
                else:
                    memory_list_trustee.append(des_str)

            

            # if "Failed" in des_str:
            #     if des_str.split("Investor is")[1].split("and")[0].strip() == self.name:
            #         memory_list_investor.append(des_str)
            #     else:
            #         memory_list_trustee.append(des_str)
            elif "Success" in des_str:
                investor_name = ""
                
                # Success investment: investor is AAA, trustee is BBB
                if "investor is" in des_str and "trustee is" in des_str:
                    investor_name = des_str.split("investor is")[1].split("trustee is")[0].strip().strip(",")
                elif "Investor is" in des_str and "Trustee is" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and Trustee is")[0].strip().strip(",")
                elif "Investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and")[0].strip().strip(",")
                elif "investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("investor is")[1].split("and")[0].strip().strip(",")


                if investor_name == self.name:
                    memory_list_investor.append(des_str)
                else:
                    memory_list_trustee.append(des_str)

        if len(memory_list_investor) >= 3:
            memory_list_investor = memory_list_investor[-3:]
        if len(memory_list_trustee) >= 3:
            memory_list_trustee = memory_list_trustee[-3:]
        return memory_list_investor, memory_list_trustee
    



    def get_latest_memory_list_brief(self):
        id_list = list(self.associativeMemory.event_id_to_node.keys())
        sorted_id_list = sorted(id_list, reverse=False)
        memory_list_investor = []
        memory_list_trustee = []
        for id in sorted_id_list:
            # if self.event_id_to_node[id]["description"].split("investor is")[-1].split("trustee is")[0].strip().strip(",")
            ob = self.associativeMemory.event_id_to_node[id]
            if type(ob) is dict:
                des_str = ob["description"]
            else:
                des_str = ob.description
            brief_des = des_str.split('\n')[0].strip()

            brief_des = des_str.split('\n')[0].strip()

            if "Failed" in des_str:
                investor_name = ""
                
                # Failed investment: investor is AAA, trustee is BBB
                if "investor is" in des_str and "trustee is" in des_str:
                    investor_name = des_str.split("investor is")[1].split("trustee is")[0].strip().strip(",")
                # Failed investment. Investor is AAA and Trustee is BBB.
                elif "Investor is" in des_str and "Trustee is" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and Trustee is")[0].strip().strip(",")
                elif "Investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and")[0].strip().strip(",")
                elif "investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("investor is")[1].split("and")[0].strip().strip(",")

                if investor_name == self.name:
                    memory_list_investor.append(brief_des)
                else:
                    memory_list_trustee.append(brief_des)

            elif "Success" in des_str:
                investor_name = ""
                
                # Success investment: investor is AAA, trustee is BBB
                if "investor is" in des_str and "trustee is" in des_str:
                    investor_name = des_str.split("investor is")[1].split("trustee is")[0].strip().strip(",")
                elif "Investor is" in des_str and "Trustee is" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and Trustee is")[0].strip().strip(",")
                elif "Investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("Investor is")[1].split("and")[0].strip().strip(",")
                elif "investor is" in des_str and "and" in des_str:
                    investor_name = des_str.split("investor is")[1].split("and")[0].strip().strip(",")

                if investor_name == self.name:
                    memory_list_investor.append(brief_des)
                else:
                    memory_list_trustee.append(brief_des)
                
        if len(memory_list_investor) >= 5:
            memory_list_investor = memory_list_investor[-5:]
        if len(memory_list_trustee) >= 5:
            memory_list_trustee = memory_list_trustee[-5:]
        return memory_list_investor, memory_list_trustee
    



    def update_interaction_memory(self, role, memory):
        if len(self.interaction_memory[role]) >= 1:
            self.interaction_memory[role].pop(0)
        self.interaction_memory[role].append(memory)

    def get_interaction_memory(self, role):
        return self.interaction_memory[role]

    def get_observation_memory(self, name, role):
        if f"{name}:{role}" in self.scratch.observed.keys():
            return self.scratch.observed[f"{name}:{role}"]
        else:
            return None

    def update_observation_memory(self, name, role, memory):
        if f"{name}:{role}" in self.scratch.observed.keys():
            self.scratch.observed[f"{name}:{role}"].append(memory)
        else:
            self.scratch.observed[f"{name}:{role}"] = []
            self.scratch.observed[f"{name}:{role}"].append(memory)

    def clear_observation_memory(self):
        self.scratch.observed = {}

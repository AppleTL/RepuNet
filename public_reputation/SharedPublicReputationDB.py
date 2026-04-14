# public_reputation/db.py
# create global publicreputationDB
# from public_reputation import publicreputationDB
from __future__ import annotations
import json
import os
from typing import Optional
from pathlib import Path




import os
import sys

# Get the path to the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the *parent* of the current directory (which is 'parent_directory') to the path
# ../../
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

# Now, the import should work because 'reputation' is a package in sys.path
from reputation.global_methods import *



class PublicReputationDB:
    def __init__(self, f_saved) -> None:
        self.public_reputations = dict()            # current
        self.out_of_date_public_reputations = dict()# history
        self.public_reputations_count = 0
        self.NEUTRAL_NUMERICAL = (0.2, 0.2, 0.2, 0.2, 0.2)
        self.save_folder = f_saved
        main_file = f"{f_saved}/public_reputation_database.json"
        archive_file = f"{f_saved}/out_of_date_public_reputation_database.json"

        print(f"INIT PublicReputationDB: {f_saved}")

        if check_if_file_exists(main_file):
            print("GNS FUNCTION: <PublicReputationDB__init__> - Loading existing DB")
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    public_reputations_load = json.load(f)
                
                self.public_reputations_count = len(public_reputations_load)
                self.public_reputations = public_reputations_load
                print(f"[PublicReputationDB] successfully load history: {self.public_reputations_count} records")
            except json.JSONDecodeError:
                print("[PublicReputationDB] doesn't exist or is damaged, it will be set to empty.")
                self.public_reputations = {}
                self._save_main()
        else:
            print("[PublicReputationDB] doesn't exist and is being created...")
            self._save_main()

        if check_if_file_exists(archive_file):
            print("GNS FUNCTION: <out_of_date_PublicReputationDB__init__> - Loading archive")
            try:
                with open(archive_file, 'r', encoding='utf-8') as f:
                    out_of_date_public_reputations = json.load(f)
                self.out_of_date_public_reputations = out_of_date_public_reputations
            except json.JSONDecodeError:
                print("[PublicReputationDB] is damaged, it will be set to empty.")
                self.out_of_date_public_reputations = {}
                self._save_archive()
        else:
            print("[PublicReputationDB] doesn't exist and is being created...")
            self._save_archive() 

    def _save_main(self):
        path = f"{self.save_folder}/public_reputation_database.json"
        os.makedirs(self.save_folder, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.public_reputations, f, indent=4, ensure_ascii=False)
        print(f"[PublicReputationDB] has been saved → {path} ({len(self.public_reputations)} records)")

    def _save_archive(self):
        path = f"{self.save_folder}/out_of_date_public_reputation_database.json"
        os.makedirs(self.save_folder, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.out_of_date_public_reputations, f, indent=4, ensure_ascii=False)
        print(f"[PublicReputationDB] has been saved → {path}")




    def get_target_public_reputation(self, target_index, role):
        target_public_reputation = {}
        for key, reputation in self.public_reputations.items():
            if role.lower() in key.lower():
                if (
                    target_index == reputation["ID"]
                    or target_index == reputation["name"]
                ):
                    target_public_reputation[key] = reputation
        return target_public_reputation


    def get_all_public_reputations(self, role, self_id, with_self=False):
        role = role.capitalize()
        all_public_reputations = dict()
        for key, public_reputation in self.public_reputations.items():
            if with_self and role in key:
                all_public_reputations[key] = public_reputation
            if f"{role}_{self_id}" != key and role in key:
                all_public_reputations[key] = public_reputation
        return all_public_reputations

    # update_individual_public_reputation(target_public_reputation, step, reason="update")
    def update_individual_public_reputation(self, reputation, curr_step, reason):
        print("UPDATING INDIVIDUAL PUBLIC REPUTATION")
        for key in reputation.keys():
            if key in self.public_reputations.keys():
                pre_reputation = self.public_reputations[key]
                pre_reputation["reason"] = reason
                self.out_of_date_public_reputations[key + f"_pre_{curr_step}"] = pre_reputation
                self.public_reputations[key] = reputation[key]
                # print("pre_reputation:" + str(pre_reputation))
                # print("public_reputation:" + str(self.public_reputations))
            else:
                self.public_reputations[key] = reputation[key]
                self.public_reputations_count += 1
                # print(str(self.public_reputations))
        self._save_main()
        self._save_archive()
        # self.update_or_create(reputation, curr_step, reason)


    def initialize_neutral_reputations(self, personas, role, scenario):
            if self.public_reputations_count > 0:
                print("[PublicReputationDB] record exists, skipping neutral initialization.")
                return

            print("[PublicReputationDB] neutrally initializing...")
            role_cap = role.capitalize()
            for persona in personas:
                key = f"{role_cap}_{persona.scratch.ID}"
                if key in self.public_reputations:
                    continue
                record = {
                    "ID": persona.scratch.ID,
                    "name": persona.scratch.name,
                    "role": role,
                    "scenario": scenario,
                    "content": "This individual has a neutral public reputation at the start of the scenario.",
                    "numerical record": str(self.NEUTRAL_NUMERICAL),
                    "last_update_step": 0,
                    "last_update_reason": "initialization",
                    "tag": "public"
                }
                self.public_reputations[key] = record
                self.public_reputations_count += 1

            self._save_main()
            print(f"[PublicReputationDB] initialized  neutral records for {len(personas)} {role} ")


    def add_initialize_neutral_reputations(self, personas, role, scenario):
        role_cap = role.capitalize()
        
        already_has_role = any(role_cap in key for key in self.public_reputations.keys())
        
        if already_has_role:
            print(f"[PublicReputationDB] {role_cap} records exist, skipping initialization.")
            return

        print("[PublicReputationDB] neutrally initializing...")
        for persona in personas:
            key = f"{role_cap}_{persona.scratch.ID}"
            if key in self.public_reputations:
                continue
            record = {
                "ID": persona.scratch.ID,
                "name": persona.scratch.name,
                "role": role,
                "scenario": scenario,
                "content": "This individual has a neutral public reputation at the start of the scenario.",
                "numerical record": str(self.NEUTRAL_NUMERICAL),
                "last_update_step": 0,
                "last_update_reason": "initialization",
                "tag": "public"
            }
            self.public_reputations[key] = record
            self.public_reputations_count += 1

        self._save_main()
        print(f"[PublicReputationDB] initialized  neutral records for {len(personas)} {role} ")


    def update_or_create(self, new_data, step, reason="update"):
        for key, incoming_record in new_data.items():
            if key not in self.public_reputations:
                print(f"[PublicReputationDB] 创建新公共声誉记录: {key}")
                new_entry = incoming_record.copy()
                new_entry["last_update_step"] = step
                new_entry["last_update_reason"] = reason
                
                self.public_reputations[key] = new_entry
                self.public_reputations_count += 1
                
            else:
                old_record = self.public_reputations[key]
                archived_key = f"{key}_pre_{step}"
                self.out_of_date_public_reputations[archived_key] = old_record.copy()
                has_changed = False
                for field, new_val in incoming_record.items():
                    if field in ["last_update_step", "last_update_reason"]:
                        continue
                    
                    old_val = old_record.get(field)
                    
                    if old_val != new_val:
                        print(f"[PublicReputationDB] 更新 {key} 的 {field}:")
                        print(f"  旧值: {old_val}")
                        print(f"  新值: {new_val} (原因: {reason})")
                        
                        old_record[field] = new_val
                        has_changed = True
                old_record["last_update_step"] = step
                old_record["last_update_reason"] = reason
                
                if not has_changed:
                    print(f"[PublicReputationDB] {key} processed with no field changes.")

        self._save_main()
        self._save_archive()

    
    def ID_get_investor_role(self, target_ID, target_persona_role):
        for key, reputation in self.public_reputations.items():
            if str(target_ID) in key.lower():
                key = f"{target_persona_role}_{target_ID}"
                reputation["role"] = target_persona_role



def restore_publicreputation_db_from_step(sim_folder, global_db_save_path):
    personas_dir = os.path.join(sim_folder, "personas")
    restored_db_data = {}
    if not os.path.exists(personas_dir):
        print(f"[Warning] Personas directory not found at {personas_dir}")
        return

    for persona_name in os.listdir(personas_dir):
        persona_path = os.path.join(personas_dir, persona_name)
        if not os.path.isdir(persona_path):
            continue

        rep_file = os.path.join(persona_path, "reputation", "public_reputation.json")
        if not os.path.exists(rep_file):
            continue

        try:
            with open(rep_file, "r", encoding="utf-8") as f:
                persona_rep_data = json.load(f)

            for role_key, inner_data in persona_rep_data.items():
                for record_id, record_content in inner_data.items():
                    restored_db_data[record_id] = record_content

        except Exception as e:
            print(f"[Error] Failed to read or parse {rep_file}: {e}")

    os.makedirs(os.path.dirname(global_db_save_path), exist_ok=True)
    
    try:
        with open(global_db_save_path, "w", encoding="utf-8") as out_file:
            json.dump(restored_db_data, out_file, indent=4)
        print(f"[Success] Public Reputation DB successfully rolled back from {sim_folder}")
    except Exception as e:
        print(f"[Error] Failed to write restored DB to {global_db_save_path}: {e}")

    return restored_db_data




def get_d_connect(init_persona, G):
    d_connect_list = []
    for edge in G.edges():
        if edge[0] == init_persona.name:
            if G.has_edge(edge[1], init_persona.name):
                d_connect_list.append(edge[1])
    return d_connect_list


from typing import Optional

_instance: Optional[PublicReputationDB] = None

def init_public_reputation_db(f_saved) -> PublicReputationDB:
    global _instance
    if _instance is None:
        _instance = PublicReputationDB(f_saved)
        print(f"[PublicReputationDB] Global publicreputationDB initialized → {f_saved}")
    return _instance

def _get_instance() -> PublicReputationDB:
    if _instance is None:
        raise RuntimeError("Please call init_public_reputation_db() first to initialize the public reputation database")
    return _instance

class public_db:
    def __getattr__(self, name):
        return getattr(_get_instance(), name)
    def __call__(self, *args, **kwargs):
        return _get_instance()
    def __repr__(self):
        # print(public_db)
        return f"<Global publicreputationDB: {len(_get_instance().public_reputations)} records>"
    
publicreputationDB = public_db()
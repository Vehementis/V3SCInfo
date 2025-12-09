"""
V3SCInfo - Star Citizen Game.log Parser Module
By V3h3m3ntis for the Hiv3mind Community

Core parsing engine for extracting gameplay statistics, performance metrics,
and session information from Star Citizen Game.log files.
"""

import re
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class SessionInfo:
    """Information about the current game session"""
    player_name: str = ""
    player_geid: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    branch: str = ""
    game_version: str = ""
    map_name: str = ""
    uptime_seconds: float = 0.0


@dataclass
class TransactionItem:
    """Individual item transaction record"""
    item_name: str = ""
    transaction_type: str = ""  # "purchase" or "sale"
    price: float = 0.0
    quantity: int = 1
    timestamp: Optional[datetime] = None
    location: str = ""


@dataclass
class MissionRecord:
    """Individual mission completion/failure record"""
    mission_id: str = ""
    player_name: str = ""
    player_id: str = ""
    completion_type: str = ""  # "Complete", "Abandon", "Fail"
    reason: str = ""
    timestamp: Optional[datetime] = None


@dataclass
class MissionInfo:
    """Mission tracking information"""
    missions: List[MissionRecord] = None
    missions_completed: int = 0
    missions_abandoned: int = 0
    missions_failed: int = 0
    
    def __post_init__(self):
        if self.missions is None:
            self.missions = []


@dataclass
class InventoryInfo:
    """Inventory and transaction tracking (placeholder for future implementation)"""
    transactions: List[TransactionItem] = None
    total_money_earned: float = 0.0
    total_money_spent: float = 0.0
    net_profit: float = 0.0
    total_items_purchased: int = 0
    total_items_sold: int = 0
    
    def __post_init__(self):
        if self.transactions is None:
            self.transactions = []


@dataclass
class GameStats:
    """Complete game statistics container"""
    session: SessionInfo
    inventory: InventoryInfo
    missions: MissionInfo
    last_update: Optional[datetime] = None


class SCLogParser:
    """V3SCInfo - Star Citizen Game.log parser by V3h3m3ntis"""
    
    def __init__(self):
        self.stats = GameStats(
            session=SessionInfo(),
            inventory=InventoryInfo(),
            missions=MissionInfo()
        )
        self.patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for log parsing"""
        return {
            # Basic parsing patterns
            'timestamp': re.compile(r'<([0-9T:.-]+Z?)>'),
            'log_level': re.compile(r'\[([^\]]+)\]'),
            'log_type': re.compile(r'<([0-9T:.-]+Z?)>[^<]*<([^>]+)>'),  # Capture both timestamp and log type in one operation
            
            # One-time session info patterns
            'player_info': re.compile(r'nickname="([^"]*)".*?playerGEID=(\d+)'),
            'branch': re.compile(r'Branch:\s+([\w.-]+)'),
            'game_version': re.compile(r'ProductVersion:\s+([\d.]+)'),
            
            'uptime': re.compile(r'uptime_secs=([\d.]+)'),
            
            # Transaction-specific patterns (only applied when log_type matches)
            'shop_buy_transaction': re.compile(r'shopName\[([^\]]+)\].*?client_price\[([\d.]+)\].*?itemName\[([^\]]+)\].*?quantity\[([\d]+)\]'),
            'shop_sell_transaction': re.compile(r'shopName\[([^\]]+)\].*?client_price\[([\d.]+)\].*?itemName\[([^\]]+)\].*?quantity\[([\d]+)\]'),
            'standard_buy_transaction': re.compile(r'shopName\[([^\]]+)\].*?client_price\[([\d.]+)\].*?itemName\[([^\]]+)\].*?quantity\[([\d]+)\]'),
            'standard_sell_transaction': re.compile(r'shopName\[([^\]]+)\].*?client_price\[([\d.]+)\].*?itemName\[([^\]]+)\].*?quantity\[([\d]+)\]'),
            
            # Commodity trading patterns
            'commodity_sell_transaction': re.compile(r'shopName\[([^\]]+)\].*?amount\[([\d.]+)\].*?resourceGUID\[([^\]]+)\].*?quantity\[([\d]+)\]'),
            'commodity_buy_transaction': re.compile(r'shopName\[([^\]]+)\].*?price\[([\d.]+)\].*?resourceGUID\[([^\]]+)\].*?quantity\[([\d.]+) cSCU\]'),
            
            # Channel Created specific patterns (extract multiple pieces of info)
            'channel_created': re.compile(r'map="([^"]*)".*?nickname="([^"]*)".*?playerGEID=(\d+)'),
            'channel_disconnected': re.compile(r'uptime_secs=([\d.]+)'),
            
            # Mission patterns
            'mission_end': re.compile(r'MissionId\[([^\]]+)\]\s+Player\[([^\]]+)\]\s+PlayerId\[([^\]]+)\]\s+CompletionType\[([^\]]+)\]\s+Reason\[([^\]]+)\]'),
        }
    
    def parse_line(self, line: str) -> bool:
        """Parse a single log line and update stats - optimized approach"""
        if not line.strip():
            return False
            
        # Extract timestamp and log type together (most efficient)
        log_type_match = self.patterns['log_type'].search(line)
        if log_type_match:
            # Extract timestamp from the same match
            try:
                timestamp_str = log_type_match.group(1)
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                self.stats.last_update = timestamp
                
                # Set session start time if not set
                if not self.stats.session.start_time:
                    self.stats.session.start_time = timestamp
                    
            except ValueError:
                pass  # Invalid timestamp format
            
            log_type = log_type_match.group(2)
            
            # Use switch-case like logic to handle specific log types
            if log_type == "CEntityComponentShopUIProvider::SendShopBuyRequest":
                self._handle_shop_ui_buy_request(line)
                return True
            elif log_type == "CEntityComponentShopUIProvider::SendShopSellRequest":
                self._handle_shop_ui_sell_request(line)
                return True
            elif log_type == "CEntityComponentShoppingProvider::SendStandardItemBuyRequest":
                self._handle_shopping_provider_buy_request(line)
                return True
            elif log_type == "CEntityComponentShoppingProvider::SendStandardItemSellRequest":
                self._handle_shopping_provider_sell_request(line)
                return True
            elif log_type == "Channel Created":
                self._handle_channel_created(line)
                return True
            elif log_type == "Channel Disconnected":
                self._handle_channel_disconnected(line)
                return True
            elif log_type == "CEntityComponentCommodityUIProvider::SendCommoditySellRequest":
                self._handle_commodity_sell_request(line)
                return True
            elif log_type == "CEntityComponentCommodityUIProvider::SendCommodityBuyRequest":
                self._handle_commodity_buy_request(line)
                return True
            elif log_type == "EndMission":
                self._handle_end_mission(line)
                return True
            # Add more log type handlers here as needed
        else:
            # Extract timestamp separately for lines without log types
            timestamp_match = self.patterns['timestamp'].search(line)
            if timestamp_match:
                try:
                    timestamp_str = timestamp_match.group(1)
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    self.stats.last_update = timestamp
                    
                    # Set session start time if not set
                    if not self.stats.session.start_time:
                        self.stats.session.start_time = timestamp
                        
                except ValueError:
                    pass  # Invalid timestamp format
        
        # Handle non-bracketed patterns (one-time session info)
        # These are typically initialization data that don't have the <Type> format
        
        # Parse branch (only if not already set)
        if not self.stats.session.branch:
            branch_match = self.patterns['branch'].search(line)
            if branch_match:
                self.stats.session.branch = branch_match.group(1)
                return True
            
        # Parse game version (only if not already set)
        if not self.stats.session.game_version:
            version_match = self.patterns['game_version'].search(line)
            if version_match:
                self.stats.session.game_version = version_match.group(1)
                return True
        
        return False
    
    def _handle_shop_ui_buy_request(self, line: str) -> None:
        """Handle CEntityComponentShopUIProvider::SendShopBuyRequest log entries"""
        match = self.patterns['shop_buy_transaction'].search(line)
        if match:
            shop_name = match.group(1)
            total_price = float(match.group(2))
            item_name = match.group(3)
            quantity = int(match.group(4))
            
            individual_price = total_price / quantity if quantity > 0 else total_price
            
            transaction = TransactionItem(
                item_name=item_name,
                transaction_type="purchase",
                price=individual_price,
                quantity=quantity,
                timestamp=self.stats.last_update,
                location=shop_name
            )
            
            self._add_transaction(transaction)
    
    def _handle_shop_ui_sell_request(self, line: str) -> None:
        """Handle CEntityComponentShopUIProvider::SendShopSellRequest log entries"""
        match = self.patterns['shop_sell_transaction'].search(line)
        if match:
            shop_name = match.group(1)
            total_price = float(match.group(2))
            item_name = match.group(3)
            quantity = int(match.group(4))
            
            individual_price = total_price / quantity if quantity > 0 else total_price
            
            transaction = TransactionItem(
                item_name=item_name,
                transaction_type="sale",
                price=individual_price,
                quantity=quantity,
                timestamp=self.stats.last_update,
                location=shop_name
            )
            
            self._add_transaction(transaction)
    
    def _handle_shopping_provider_buy_request(self, line: str) -> None:
        """Handle CEntityComponentShoppingProvider::SendStandardItemBuyRequest log entries"""
        match = self.patterns['standard_buy_transaction'].search(line)
        if match:
            shop_name = match.group(1)
            total_price = float(match.group(2))
            item_name = match.group(3)
            quantity = int(match.group(4))
            
            individual_price = total_price / quantity if quantity > 0 else total_price
            
            transaction = TransactionItem(
                item_name=item_name,
                transaction_type="purchase",
                price=individual_price,
                quantity=quantity,
                timestamp=self.stats.last_update,
                location=shop_name
            )
            
            self._add_transaction(transaction)
    
    def _handle_shopping_provider_sell_request(self, line: str) -> None:
        """Handle CEntityComponentShoppingProvider::SendStandardItemSellRequest log entries"""
        match = self.patterns['standard_sell_transaction'].search(line)
        if match:
            shop_name = match.group(1)
            total_price = float(match.group(2))
            item_name = match.group(3)
            quantity = int(match.group(4))
            
            individual_price = total_price / quantity if quantity > 0 else total_price
            
            transaction = TransactionItem(
                item_name=item_name,
                transaction_type="sale",
                price=individual_price,
                quantity=quantity,
                timestamp=self.stats.last_update,
                location=shop_name
            )
            
            self._add_transaction(transaction)
    
    def _handle_commodity_sell_request(self, line: str) -> None:
        """Handle CEntityComponentCommodityUIProvider::SendCommoditySellRequest log entries"""
        match = self.patterns['commodity_sell_transaction'].search(line)
        if match:
            shop_name = match.group(1)
            total_amount = float(match.group(2))  # Total aUEC received
            resource_guid = match.group(3)  # Using GUID as item identifier
            quantity = int(match.group(4))  # Number of items sold
            
            individual_price = total_amount / quantity if quantity > 0 else total_amount
            
            transaction = TransactionItem(
                item_name=f"Commodity-{resource_guid[:8]}",  # Shortened GUID for readability
                transaction_type="sale",
                price=individual_price,
                quantity=quantity,
                timestamp=self.stats.last_update,
                location=shop_name
            )
            
            self._add_transaction(transaction)
    
    def _handle_commodity_buy_request(self, line: str) -> None:
        """Handle CEntityComponentCommodityUIProvider::SendCommodityBuyRequest log entries"""
        match = self.patterns['commodity_buy_transaction'].search(line)
        if match:
            shop_name = match.group(1)
            total_price = float(match.group(2))  # Total aUEC spent
            resource_guid = match.group(3)  # Using GUID as item identifier
            quantity_cscu = float(match.group(4))  # Quantity in cSCU
            
            # Convert cSCU to actual quantity (divide by 100)
            actual_quantity = int(quantity_cscu / 100) if quantity_cscu >= 100 else 1
            individual_price = total_price / actual_quantity if actual_quantity > 0 else total_price
            
            transaction = TransactionItem(
                item_name=f"Commodity-{resource_guid[:8]}",  # Shortened GUID for readability
                transaction_type="purchase",
                price=individual_price,
                quantity=actual_quantity,
                timestamp=self.stats.last_update,
                location=shop_name
            )
            
            self._add_transaction(transaction)
    
    def _handle_channel_created(self, line: str) -> None:
        """Handle Channel Created log entries for map info and player info"""
        # Try to extract all info at once (map, nickname, playerGEID)
        full_match = self.patterns['channel_created'].search(line)
        if full_match:
            self.stats.session.map_name = full_match.group(1)
            self.stats.session.player_name = full_match.group(2)
            self.stats.session.player_geid = full_match.group(3)
    
    def _handle_channel_disconnected(self, line: str) -> None:
        """Handle Channel Disconnected log entries for session end and final uptime"""
        if self.stats.last_update:
            self.stats.session.end_time = self.stats.last_update
        
        # Extract final uptime if available
        uptime_match = self.patterns['channel_disconnected'].search(line)
        if uptime_match:
            self.stats.session.uptime_seconds = float(uptime_match.group(1))
    
    def _handle_end_mission(self, line: str) -> None:
        """Handle EndMission log entries for mission completion tracking"""
        match = self.patterns['mission_end'].search(line)
        if match:
            mission_id = match.group(1)
            player_name = match.group(2)
            player_id = match.group(3)
            completion_type = match.group(4)
            reason = match.group(5)
            
            mission = MissionRecord(
                mission_id=mission_id,
                player_name=player_name,
                player_id=player_id,
                completion_type=completion_type,
                reason=reason,
                timestamp=self.stats.last_update
            )
            
            self._add_mission(mission)
    
    def _add_transaction(self, transaction: TransactionItem) -> None:
        """Add a transaction and update inventory statistics"""
        self.stats.inventory.transactions.append(transaction)
        
        total_cost = transaction.price * transaction.quantity
        
        if transaction.transaction_type == "purchase":
            self.stats.inventory.total_money_spent += total_cost
            self.stats.inventory.total_items_purchased += transaction.quantity
        elif transaction.transaction_type == "sale":
            self.stats.inventory.total_money_earned += total_cost
            self.stats.inventory.total_items_sold += transaction.quantity
        
        # Update net profit
        self.stats.inventory.net_profit = (
            self.stats.inventory.total_money_earned - 
            self.stats.inventory.total_money_spent
        )
    
    def _add_mission(self, mission: MissionRecord) -> None:
        """Add a mission and update mission statistics"""
        self.stats.missions.missions.append(mission)
        
        # Update mission counters
        if mission.completion_type.lower() == "complete":
            self.stats.missions.missions_completed += 1
        elif mission.completion_type.lower() == "abandon":
            self.stats.missions.missions_abandoned += 1
        else:
            # Count any other completion type as failed
            self.stats.missions.missions_failed += 1
    
    def get_recent_transactions(self, limit: int = 10) -> List[TransactionItem]:
        """Get the most recent transactions"""
        return self.stats.inventory.transactions[-limit:] if self.stats.inventory.transactions else []
    
    def get_recent_missions(self, limit: int = 10) -> List[MissionRecord]:
        """Get the most recent missions"""
        return self.stats.missions.missions[-limit:] if self.stats.missions.missions else []
    
    def get_transaction_summary(self) -> str:
        """Get a formatted summary of recent transactions"""
        recent = self.get_recent_transactions(5)
        if not recent:
            return "No recent transactions"
        
        summary = "=== Recent Transactions ===\n"
        for trans in reversed(recent):  # Show most recent first
            time_str = trans.timestamp.strftime('%H:%M:%S') if trans.timestamp else 'Unknown'
            action = "Bought" if trans.transaction_type == "purchase" else "Sold"
            total_cost = trans.price * trans.quantity
            summary += f"{time_str} - {action} {trans.quantity}x {trans.item_name} for {total_cost:,.0f} aUEC at {trans.location}\n"
        
        return summary.strip()
    
    def get_mission_summary(self) -> str:
        """Get a formatted summary of recent missions"""
        recent = self.get_recent_missions(5)
        if not recent:
            return "No recent missions"
        
        summary = "=== Recent Missions ===\n"
        for mission in reversed(recent):  # Show most recent first
            time_str = mission.timestamp.strftime('%H:%M:%S') if mission.timestamp else 'Unknown'
            status = mission.completion_type
            summary += f"{time_str} - {status}: {mission.player_name} - {mission.reason} (ID: {mission.mission_id[:8]}...)\n"
        
        return summary.strip()
    
    def parse_file(self, file_path: str, start_from_end: bool = True) -> None:
        """Parse the entire log file or from a specific position"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if start_from_end:
                    # Read from end to get current session data
                    lines = f.readlines()
                    # Process last 1000 lines to get current state
                    for line in lines[-1000:]:
                        self.parse_line(line)
                else:
                    # Read entire file
                    for line in f:
                        self.parse_line(line)
        except Exception as e:
            print(f"Error parsing file: {e}")
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Get statistics as a dictionary"""
        stats_dict = asdict(self.stats)
        
        # Convert datetime objects to strings for JSON serialization
        if stats_dict['session']['start_time']:
            stats_dict['session']['start_time'] = self.stats.session.start_time.isoformat()
        if stats_dict['session']['end_time']:
            stats_dict['session']['end_time'] = self.stats.session.end_time.isoformat()
        if stats_dict['last_update']:
            stats_dict['last_update'] = self.stats.last_update.isoformat()
        
        # Convert transaction timestamps
        for i, transaction in enumerate(stats_dict['inventory']['transactions']):
            if self.stats.inventory.transactions[i].timestamp:
                transaction['timestamp'] = self.stats.inventory.transactions[i].timestamp.isoformat()
        
        # Convert mission timestamps
        for i, mission in enumerate(stats_dict['missions']['missions']):
            if self.stats.missions.missions[i].timestamp:
                mission['timestamp'] = self.stats.missions.missions[i].timestamp.isoformat()
            
        return stats_dict
    
    def get_formatted_stats(self) -> str:
        """Get formatted statistics as a string"""
        session = self.stats.session
        inv = self.stats.inventory
        missions = self.stats.missions
        
        uptime_hours = session.uptime_seconds / 3600 if session.uptime_seconds else 0
        
        return f"""
=== Star Citizen Session Stats ===
Player: {session.player_name or 'Unknown'} ({session.player_geid})
Game Version: {session.game_version} (Branch: {session.branch})
Map: {session.map_name}
Uptime: {uptime_hours:.1f} hours

=== Inventory & Trading ===

Total Earned: {inv.total_money_earned:,.0f} aUEC
Total Spent: {inv.total_money_spent:,.0f} aUEC
Net Profit: {inv.net_profit:,.0f} aUEC
Items Purchased: {inv.total_items_purchased}
Items Sold: {inv.total_items_sold}
Recent Transactions: {len(inv.transactions)}

{self.get_transaction_summary()}

=== Missions ===

Completed: {missions.missions_completed}
Abandoned: {missions.missions_abandoned}
Failed: {missions.missions_failed}
Total Missions: {len(missions.missions)}

{self.get_mission_summary()}

Last Update: {self.stats.last_update.strftime('%H:%M:%S') if self.stats.last_update else 'Never'}
"""

    def reset_stats(self) -> None:
        """Reset all statistics to default values"""
        self.stats = GameStats(
            session=SessionInfo(),
            inventory=InventoryInfo(),
            missions=MissionInfo()
        )


if __name__ == "__main__":
    # Test the parser with the game log
    parser = SCLogParser()
    log_path = "Game.log"  # Adjust path as needed
    
    print("Parsing Star Citizen Game.log...")
    parser.parse_file(log_path)
    print(parser.get_formatted_stats())

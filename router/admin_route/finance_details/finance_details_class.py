from sqlalchemy.orm import Session
from models.user import finance_details_table
from schema import finance_details


class FinanceDetails:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_bank_details(self, bank_details_data: finance_details.BankDetailsCreate):
        bank_details = self.db_session.query(finance_details_table.BankDetails).filter(
            finance_details_table.BankDetails.owner == "admin").first()
        if not bank_details:
            bank_data = finance_details_table.BankDetails(
                bank_name=bank_details_data.bank_name,
                account_name=bank_details_data.account_name,
                iban=bank_details_data.iban,
                bic=bank_details_data.bic,
                reference=bank_details_data.reference,
                owner="admin"
            )
            self.db_session.add(bank_data)
            self.db_session.commit()
            self.db_session.refresh(bank_data)
            return {"status": "success", "message": bank_data}
        else:
            return {"status": "error"}

    def edit_bank_details(self, bank_details_id: int, bank_details_data: finance_details.BankDetailsCreate):
        bank_data = self.db_session.query(finance_details_table.BankDetails).filter(
            finance_details_table.BankDetails.id == bank_details_id).first()
        if bank_data:
            for key, value in bank_details_data:
                setattr(bank_data, key, value)
            self.db_session.commit()
            self.db_session.refresh(bank_data)
            return {"status": "success", "message": bank_data}
        else:
            return None

    def create_crypto_payment_details(self, crypto_data: finance_details.CryptoCurrencyWalletCreate):
        crypto_create = finance_details_table.CryptoCurrencyWallet(
            wallet_address=crypto_data.wallet_address,
            network_chain=crypto_data.network_chain,
            preferred_token=crypto_data.preferred_token
        )
        self.db_session.add(crypto_create)
        self.db_session.commit()
        self.db_session.refresh(crypto_create)
        return {"status": "success", "message": crypto_create}

    def edit_crypto_payment_details(self, crypto_data_id: int, crypto_data: finance_details.CryptoCurrencyWalletCreate):
        data = self.db_session.query(finance_details_table.CryptoCurrencyWallet).filter(
            finance_details_table.CryptoCurrencyWallet.id == crypto_data_id).first()
        if data:
            for key, value in crypto_data:
                setattr(data, key, value)
            self.db_session.commit()
            self.db_session.refresh(data)
            return {"status": "success", "message": data}
        else:
            return None

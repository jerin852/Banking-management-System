
import streamlit as st

from database import (
    init_db,
    create_account,
    get_account,
    deposit_money,
    withdraw_money,
    list_accounts,
    get_transactions
)

from bank_account import SavingsAccount


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Jerin Bank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# 2. INITIALIZE DATABASE
# ==================================================

init_db()


# ==================================================
# 3. HELPER FUNCTIONS
# ==================================================

def format_money(amount):
    return f"₹{float(amount):,.2f}"


def navigate(page):
    st.session_state.menu = page
    st.rerun()


def load_all_transactions(accounts):
    transactions = []

    for account in accounts:
        account_number = account["Account Number"]

        account_transactions = get_transactions(account_number)

        for transaction in account_transactions:
            transaction["Account Number"] = account_number
            transaction["Account Holder"] = account["Account Holder"]

            transactions.append(transaction)

    transactions.sort(
        key=lambda item: item["Date"],
        reverse=True
    )

    return transactions


# ==================================================
# 4. SIDEBAR NAVIGATION
# ==================================================

st.sidebar.markdown(
    "<h1 style='text-align:center;'>🏦 JERIN BANK</h1>",
    unsafe_allow_html=True
)

st.sidebar.caption("DIGITAL BANKING")

st.sidebar.divider()

st.sidebar.subheader("MAIN MENU")

navigation = {
    "Dashboard": "🏠 Dashboard",
    "Create Account": "➕ Create Account",
    "Account Details": "👤 Account Details",
    "Deposit Money": "💰 Deposit Money",
    "Withdraw Money": "💸 Withdraw Money",
    "All Accounts": "👥 All Accounts",
    "Transaction History": "📊 Transaction History"
}

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"


for page, label in navigation.items():

    if st.sidebar.button(
        label,
        key=f"nav_{page}",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.menu == page
            else "secondary"
        )
    ):
        navigate(page)


st.sidebar.divider()

st.sidebar.caption("SECURE DIGITAL BANKING")
st.sidebar.caption("© 2026 JERIN BANK")


menu = st.session_state.menu


# ==================================================
# 5. DASHBOARD
# ==================================================

if menu == "Dashboard":

    accounts = list_accounts()

    total_accounts = len(accounts)

    total_balance = sum(
        float(account["Balance"])
        for account in accounts
    )

    all_transactions = load_all_transactions(accounts)

    total_deposits = sum(
        float(transaction["Amount"])
        for transaction in all_transactions
        if transaction["Transaction"] in ["OPENING", "DEPOSIT"]
    )

    total_withdrawals = sum(
        float(transaction["Amount"])
        for transaction in all_transactions
        if transaction["Transaction"] == "WITHDRAWAL"
    )

    # Dashboard heading

    st.caption("JERIN BANK / OVERVIEW")

    st.title("Good Morning! 👋")

    st.write("Welcome to your digital banking dashboard.")

    # Total balance card

    st.html(f"""
    <div style="
        background: linear-gradient(120deg, #172c52, #315b9b);
        padding: 35px;
        border-radius: 20px;
        color: white;
        box-shadow: 0 8px 25px rgba(23,44,82,0.18);
        margin: 15px 0;
    ">

        <p style="
            color: #d4e1ff;
            font-size: 15px;
            margin: 0;
        ">
            TOTAL ACCOUNT BALANCE
        </p>

        <h1 style="
            color: white;
            font-size: 42px;
            margin: 12px 0;
        ">
            {format_money(total_balance)}
        </h1>

        <p style="color: #e1e8ff; margin: 0;">
            Across all registered accounts
        </p>

        <div style="
            display: flex;
            justify-content: space-between;
            margin-top: 28px;
            color: #e1e8ff;
            font-size: 13px;
        ">
            <span>JERIN BANK</span>
            <span>SECURE DIGITAL BANKING</span>
        </div>

    </div>
    """)

    # Financial overview

    st.subheader("Financial Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Accounts",
            total_accounts
        )

    with col2:
        st.metric(
            "Total Deposits",
            format_money(total_deposits)
        )

    with col3:
        st.metric(
            "Total Withdrawals",
            format_money(total_withdrawals)
        )

    # Quick actions

    st.subheader("Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("➕ Create Account", use_container_width=True):
            navigate("Create Account")

    with col2:
        if st.button("💰 Deposit Money", use_container_width=True):
            navigate("Deposit Money")

    with col3:
        if st.button("💸 Withdraw Money", use_container_width=True):
            navigate("Withdraw Money")

    with col4:
        if st.button("👥 All Accounts", use_container_width=True):
            navigate("All Accounts")

    # Recent transactions

    st.subheader("Recent Transactions")

    if all_transactions:

        st.dataframe(
            all_transactions[:5],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No transactions available yet.")

    # Account overview

    st.subheader("Account Overview")

    if accounts:

        for account in accounts:

            with st.container(border=True):

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Account Holder**")
                    st.write(account["Account Holder"])

                    st.write("**Account Number**")
                    st.write(f'#{account["Account Number"]}')

                with col2:
                    st.write("**Available Balance**")
                    st.subheader(format_money(account["Balance"]))

    else:
        st.info("No accounts found. Create your first account.")


# ==================================================
# 6. CREATE ACCOUNT
# ==================================================

elif menu == "Create Account":

    st.title("➕ Create New Account")

    st.write("Register a new customer bank account.")

    with st.form("create_account_form"):

        name = st.text_input(
            "Account Holder Name",
            placeholder="Enter full name"
        )

        balance = st.number_input(
            "Initial Deposit (₹)",
            min_value=0.0,
            value=0.0,
            step=500.0
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

        if submitted:

            try:
                account_number = create_account(name, balance)

                st.success("Account created successfully!")

                st.write("Your Account Number:")
                st.code(str(account_number))

            except (ValueError, TypeError) as error:
                st.error(str(error))


# ==================================================
# 7. ACCOUNT DETAILS
# ==================================================

elif menu == "Account Details":

    st.title("👤 Account Details")

    account_number = st.number_input(
        "Enter Account Number",
        min_value=1001,
        step=1
    )

    if st.button("Search Account"):

        try:
            account = get_account(account_number)

            st.success("Account found successfully!")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Account Holder",
                    account["name"]
                )

            with col2:
                st.metric(
                    "Account Balance",
                    format_money(account["balance"])
                )

            st.write("**Account Number:**", 1000 + account["id"])

            st.write("**Created At:**", account["created_at"])

            savings_account = SavingsAccount(
                account["name"],
                account["balance"]
            )

            interest = savings_account.calculate_interest()

            st.info(
                "Illustrative 5% interest: "
                + format_money(interest)
            )

        except (ValueError, TypeError) as error:
            st.error(str(error))


# ==================================================
# 8. DEPOSIT MONEY
# ==================================================

elif menu == "Deposit Money":

    st.title("💰 Deposit Money")

    st.write("Deposit money into an existing account.")

    with st.form("deposit_form"):

        account_number = st.number_input(
            "Account Number",
            min_value=1001,
            step=1
        )

        amount = st.number_input(
            "Deposit Amount (₹)",
            min_value=0.0,
            value=0.0,
            step=500.0
        )

        submitted = st.form_submit_button(
            "Deposit Money",
            use_container_width=True
        )

        if submitted:

            try:
                new_balance = deposit_money(
                    account_number,
                    amount
                )

                st.success("Deposit completed successfully!")

                st.metric(
                    "Updated Balance",
                    format_money(new_balance)
                )

            except (ValueError, TypeError) as error:
                st.error(str(error))


# ==================================================
# 9. WITHDRAW MONEY
# ==================================================

elif menu == "Withdraw Money":

    st.title("💸 Withdraw Money")

    st.write("Withdraw money from an existing account.")

    with st.form("withdraw_form"):

        account_number = st.number_input(
            "Account Number",
            min_value=1001,
            step=1
        )

        amount = st.number_input(
            "Withdrawal Amount (₹)",
            min_value=0.0,
            value=0.0,
            step=500.0
        )

        submitted = st.form_submit_button(
            "Withdraw Money",
            use_container_width=True
        )

        if submitted:

            try:
                new_balance = withdraw_money(
                    account_number,
                    amount
                )

                st.success("Withdrawal completed successfully!")

                st.metric(
                    "Remaining Balance",
                    format_money(new_balance)
                )

            except (ValueError, TypeError) as error:
                st.error(str(error))


# ==================================================
# 10. ALL ACCOUNTS
# ==================================================

elif menu == "All Accounts":

    st.title("👥 All Registered Accounts")

    accounts = list_accounts()

    if accounts:

        st.write(f"Total Accounts: **{len(accounts)}**")

        st.dataframe(
            accounts,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No accounts registered yet.")


# ==================================================
# 11. TRANSACTION HISTORY
# ==================================================

elif menu == "Transaction History":

    st.title("📊 Transaction History")

    account_number = st.number_input(
        "Enter Account Number",
        min_value=1001,
        step=1
    )

    if st.button("View Transactions"):

        try:
            account = get_account(account_number)

            transactions = get_transactions(account_number)

            st.success(
                f"Transaction history: {account['name']}"
            )

            if transactions:

                st.dataframe(
                    transactions,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No transactions found.")

        except (ValueError, TypeError) as error:
            st.error(str(error))


# ==================================================
# 12. FOOTER
# ==================================================

st.divider()

st.caption(
    "JERIN BANK | DIGITAL BANKING MANAGEMENT SYSTEM"
)

st.caption(
    "Built with Python, OOP, SQLite and Streamlit"
)

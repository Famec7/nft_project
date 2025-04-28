def cancel_expired_listings():
    """
    This function is called by the cron job to cancel expired NFT listings.
    It checks for expired listings in the database and calls the smart contract
    to cancel them.
    """
    from django.core.management import call_command
    call_command('cancel_expired_listings')
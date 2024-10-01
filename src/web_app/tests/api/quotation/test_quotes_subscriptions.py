import pytest
import sqlalchemy as sa
from httpx import AsyncClient
from pydantic_core import from_json
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.quotation.schemas import DashboardSubscriptions
from constants.constants import moex_names_parsing_list
from db import models


@pytest.mark.asyncio
async def test_get_user_list_subs_without_subs(
        _async_client: AsyncClient,
        _async_session: AsyncSession,
):
    user_id = 123
    user_role = models.UserRole(
        name="test",
        description="test",
    )

    _async_session.add(user_role)
    await _async_session.flush()

    user = models.RegisteredUser(
        user_id=user_id,
        username='name',
        full_name='full_name',
        user_type='type',
        user_status='status',
        role_id=user_role.id,
    )
    _async_session.add(user)

    section = models.QuotesSections(
        name=(section_name := 'test')
    )
    _async_session.add(section)
    await _async_session.flush()
    _async_session.add(
        models.Quotes(
            name=(quote_name := 'test_quote'),
            quotes_section_id=section.id
        )
    )
    await _async_session.commit()

    response = await _async_client.get(f'/api/v1/quotation/dashboard/{user_id}/subscriptions')
    assert response.status_code == 200

    dashboard_subscriptions = DashboardSubscriptions.model_validate(from_json(response.text))
    assert len(dashboard_subscriptions.subscription_sections) == 1
    assert (section := dashboard_subscriptions.subscription_sections[0]).section_name == section_name
    assert len(section.subscription_items) == 1
    assert section.subscription_items[0].name == quote_name
    assert not section.subscription_items[0].active
    assert section.subscription_items[0].id != 0


@pytest.mark.asyncio
async def test_get_user_list_subs_with_subs(
        _async_client: AsyncClient,
        _async_session: AsyncSession,
):
    user_id = 123
    user_role = models.UserRole(
        name="test",
        description="test",
    )

    _async_session.add(user_role)
    await _async_session.flush()

    user = models.RegisteredUser(
        user_id=user_id,
        username='name',
        full_name='full_name',
        user_type='type',
        user_status='status',
        role_id=user_role.id,
    )
    _async_session.add(user)

    section = models.QuotesSections(
        name=(section_name := 'test')
    )
    _async_session.add(section)
    await _async_session.flush()
    quote = models.Quotes(
        name=(quote_name := 'test_quote'),
        quotes_section_id=section.id
    )
    _async_session.add(quote)
    await _async_session.flush()
    _async_session.add(
        models.UsersQuotesSubscriptions(
            user_id=user_id,
            quote_id=quote.id,
            view_size=models.SizeEnum.TEXT,
        )
    )
    await _async_session.commit()

    response = await _async_client.get(f'/api/v1/quotation/dashboard/{user_id}/subscriptions')
    assert response.status_code == 200

    dashboard_subscriptions = DashboardSubscriptions.model_validate(from_json(response.text))
    assert len(dashboard_subscriptions.subscription_sections) == 1
    assert (section := dashboard_subscriptions.subscription_sections[0]).section_name == section_name
    assert len(section.subscription_items) == 1
    assert section.subscription_items[0].name == quote_name
    assert section.subscription_items[0].active
    assert section.subscription_items[0].type == models.SizeEnum.TEXT
    assert section.subscription_items[0].id != 0


@pytest.mark.asyncio
async def test_update_user_subs(
        _async_client: AsyncClient,
        _async_session: AsyncSession,
):
    user_id = 123
    user_role = models.UserRole(
        name="test",
        description="test",
    )

    _async_session.add(user_role)
    await _async_session.flush()

    user = models.RegisteredUser(
        user_id=user_id,
        username='name',
        full_name='full_name',
        user_type='type',
        user_status='status',
        role_id=user_role.id,
    )
    _async_session.add(user)

    section = models.QuotesSections(
        name='test'
    )
    _async_session.add(section)
    await _async_session.flush()
    quote1 = models.Quotes(
        name='test_quote1',
        quotes_section_id=section.id
    )
    _async_session.add(quote1)
    await _async_session.flush()
    quote2 = models.Quotes(
        name='test_quote2',
        quotes_section_id=section.id
    )
    _async_session.add(quote2)

    await _async_session.flush()
    _async_session.add(
        models.UsersQuotesSubscriptions(
            user_id=user_id,
            quote_id=quote1.id,
            view_size=models.SizeEnum.TEXT,
        )
    )
    await _async_session.commit()

    response = await _async_client.get(f'/api/v1/quotation/dashboard/{user_id}/subscriptions')
    assert response.status_code == 200
    dashboard_subscriptions = DashboardSubscriptions.model_validate(from_json(response.text))

    assert dashboard_subscriptions.subscription_sections[0].subscription_items[1].id == quote2.id
    dashboard_subscriptions.subscription_sections[0].subscription_items[1].active = True

    update_request = await _async_client.put(
        f'/api/v1/quotation/dashboard/{user_id}/subscriptions',
        json=dashboard_subscriptions.model_dump()
    )
    assert update_request.status_code == 202

    response = await _async_client.get(f'/api/v1/quotation/dashboard/{user_id}/subscriptions')
    assert response.status_code == 200
    dashboard_subscriptions = DashboardSubscriptions.model_validate(from_json(response.text))

    assert dashboard_subscriptions.subscription_sections[0].subscription_items[1].id == quote2.id
    assert dashboard_subscriptions.subscription_sections[0].subscription_items[1].active

    stmt = await _async_session.execute(
        sa.select(models.UsersQuotesSubscriptions)
        .filter(models.UsersQuotesSubscriptions.user_id == user_id)
    )
    user_subs_list = stmt.scalars().fetchall()
    assert len(user_subs_list) == 2


@pytest.mark.asyncio
async def test_delete_user_subs():
    pass


@pytest.mark.asyncio
async def test_add_user_subs():
    pass


@pytest.mark.asyncio
async def test_get_cbr_quotes(
        _async_session: AsyncSession
):
    from utils.quotes import load_CBR_quotes

    await load_CBR_quotes(_async_session)

    stmt = await _async_session.execute(sa.select(models.Quotes))
    assert len(stmt.scalars().fetchall())


@pytest.mark.asyncio
async def test_get_quote_date(
        _async_session: AsyncSession
):
    from utils.quotes import load_CBR_quotes
    from utils.quotes.updater import update_cbr_quote

    await load_CBR_quotes(_async_session)

    stmt = await _async_session.execute(sa.select(models.Quotes))
    quote = stmt.scalars().first()

    await update_cbr_quote(quote, _async_session)

    stmt = await _async_session.execute(sa.select(models.QuotesValues))
    quote_data = stmt.scalars().fetchall()
    assert len(quote_data) >= 1


@pytest.mark.asyncio
async def test_get_double_quote_date(
        _async_session: AsyncSession
):
    from utils.quotes import load_CBR_quotes
    from utils.quotes.updater import update_cbr_quote

    await load_CBR_quotes(_async_session)

    stmt = await _async_session.execute(sa.select(models.Quotes))
    quote = stmt.scalars().first()

    await update_cbr_quote(quote, _async_session)

    stmt = await _async_session.execute(sa.select(models.QuotesValues))
    quote_data = stmt.scalars().fetchall()
    quote_len = len(quote_data)

    await update_cbr_quote(quote, _async_session)

    stmt = await _async_session.execute(sa.select(models.QuotesValues))
    quote_data = stmt.scalars().fetchall()


    assert len(quote_data) == quote_len


@pytest.mark.asyncio
async def test_get_all_quote_date(
        _async_session: AsyncSession,
):
    from utils.quotes import load_CBR_quotes
    from utils.quotes.updater import update_all_cbr

    await load_CBR_quotes(_async_session)
    await update_all_cbr()

    stmt = await _async_session.execute(sa.select(models.QuotesValues))
    quote_data = stmt.scalars().fetchall()
    assert len(quote_data) >= 1


@pytest.mark.asyncio
async def test_load_moex_quotes(
        _async_client: AsyncClient,
        _async_session: AsyncSession,
):
    from utils.quotes.loader import load_moex_quotes
    from utils.quotes.updater import update_all_moex

    await load_moex_quotes()
    await update_all_moex()

    stmt = await _async_session.execute(sa.select(models.Quotes))
    quotes = stmt.scalars().fetchall()
    assert len(quotes) == len(moex_names_parsing_list)



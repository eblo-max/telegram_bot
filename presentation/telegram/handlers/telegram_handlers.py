import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from uuid import UUID

from telegram import Update
from telegram.ext import ContextTypes

from dark_archive.application.interfaces.telegram_client import ITelegramClient
from dark_archive.application.interfaces.message_gateway import IMessageGateway
from dark_archive.domain.services.case_service import CaseService
from dark_archive.domain.value_objects.message import (
    OutboundMessage,
    Button,
    MessageFormat,
)

logger = logging.getLogger(__name__)


@dataclass
class TelegramHandlers:
    """Обработчики команд Telegram бота"""

    telegram_client: ITelegramClient
    case_service: CaseService
    message_gateway: IMessageGateway

    def get_handlers(self) -> List[Callable]:
        """Возвращает список всех обработчиков команд

        Returns:
            List[Callable]: Список обработчиков
        """
        return [
            self.start_command,
            self.help_command,
            self.new_case_command,
            self.list_cases_command,
            self.case_info_command,
            self.button_handler,
        ]

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /start"""
        welcome_message = OutboundMessage(
            recipient_id=str(update.effective_chat.id),
            content=(
                "🔍 *Добро пожаловать в Dark Archive!*\n\n"
                "Я - ваш помощник в расследовании самых мрачных и загадочных дел.\n\n"
                "Доступные команды:\n"
                "/new_case - Начать новое расследование\n"
                "/list_cases - Показать список активных дел\n"
                "/case <id> - Информация о конкретном деле\n"
                "/help - Показать справку"
            ),
            format=MessageFormat.MARKDOWN,
        )
        await self.telegram_client.send_message(
            update.effective_chat.id, welcome_message
        )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /help"""
        help_message = OutboundMessage(
            recipient_id=str(update.effective_chat.id),
            content=(
                "📖 *Справка по командам:*\n\n"
                "🔍 */new_case* - Начать новое расследование\n"
                "📋 */list_cases* - Показать список активных дел\n"
                "📁 */case <id>* - Информация о конкретном деле\n"
                "❓ */help* - Показать эту справку\n\n"
                "_Для взаимодействия с локациями и уликами используйте кнопки под сообщениями._"
            ),
            format=MessageFormat.MARKDOWN,
        )
        await self.telegram_client.send_message(update.effective_chat.id, help_message)

    async def new_case_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /new_case"""
        try:
            # Проверяем инициализацию клиента и компонентов
            if not hasattr(self, "case_service") or self.case_service is None:
                logger.error("Case service not initialized")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Внутренняя ошибка: сервис не инициализирован",
                )
                return

            logger.info(
                f"Starting new case creation for chat {update.effective_chat.id}"
            )

            # Отправляем сообщение о начале создания
            await self.telegram_client.send_message(
                update.effective_chat.id,
                OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="⏳ Создаю новое расследование... Это может занять некоторое время.",
                    format=MessageFormat.MARKDOWN,
                ),
            )

            # Создаем новое расследование со средней сложностью
            logger.debug("Calling case_service.create_case")
            case = await self.case_service.create_case(difficulty=5)

            if not case:
                logger.error("Failed to create case: returned None")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Не удалось создать новое дело. Пожалуйста, попробуйте позже.",
                )
                return

            logger.info(f"Case created successfully with ID: {case.id}")

            # Формируем сообщение с информацией о новом расследовании
            keyboard_buttons = [
                [
                    Button(
                        text="🔍 Исследовать локацию",
                        callback_data=f"explore_{case.id}",
                    ),
                    Button(
                        text="🗺 Карта локаций",
                        callback_data=f"locations_{case.id}",
                    ),
                ],
                [
                    Button(
                        text="🔮 Улики",
                        callback_data=f"evidence_{case.id}",
                    ),
                    Button(
                        text="📝 Анализ",
                        callback_data=f"analyze_{case.id}",
                    ),
                ],
            ]

            message = OutboundMessage(
                recipient_id=str(update.effective_chat.id),
                content=(
                    f"🗂 *Новое дело #{case.id}*\n\n"
                    f"*Название:* {case.title}\n"
                    f"*Описание:* {case.description}\n\n"
                    "_Используйте кнопки ниже для взаимодействия с делом_"
                ),
                format=MessageFormat.MARKDOWN,
                keyboard_buttons=keyboard_buttons,
            )
            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info(f"New case information sent to chat {update.effective_chat.id}")

        except TypeError as e:
            logger.error(f"Type error in new_case_command: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Ошибка при создании дела: несоответствие типов данных",
            )
        except AttributeError as e:
            logger.error(
                f"Attribute error in new_case_command: {str(e)}", exc_info=True
            )
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Ошибка при создании дела: отсутствует необходимый атрибут",
            )
        except ValueError as e:
            logger.error(f"Value error in new_case_command: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Ошибка при создании дела: некорректное значение",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in new_case_command: {str(e)}", exc_info=True
            )
            await self._send_error_message(
                update.effective_chat.id, "❌ Произошла ошибка при создании нового дела"
            )

    async def _send_error_message(self, chat_id: int, message: str) -> None:
        """Вспомогательный метод для отправки сообщений об ошибках"""
        try:
            error_message = OutboundMessage(
                recipient_id=str(chat_id),
                content=message,
                format=MessageFormat.MARKDOWN,
            )
            await self.telegram_client.send_message(chat_id, error_message)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}", exc_info=True)

    async def list_cases_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /list_cases"""
        try:
            logger.info(f"Listing cases for chat {update.effective_chat.id}")

            # Проверяем инициализацию сервиса
            if not hasattr(self, "case_service") or self.case_service is None:
                logger.error("Case service not initialized")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Внутренняя ошибка: сервис не инициализирован",
                )
                return

            # Получаем список дел
            logger.debug("Calling case_service.list_cases")
            cases = await self.case_service.list_cases()
            logger.info(f"Retrieved {len(cases)} cases")

            if not cases:
                logger.info("No cases found")
                message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="📭 У вас пока нет активных расследований.\n\nИспользуйте /new_case чтобы начать новое!",
                    format=MessageFormat.HTML,
                )
            else:
                cases_text = "\n\n".join(
                    f"🗂 <b>Дело №{case.id}</b>\n"
                    f"<b>Название:</b> {case.title}\n"
                    f"<b>Статус:</b> {'🟢' if case.status == 'active' else '🔴'}\n"
                    f"<b>Прогресс:</b> {case.progress * 100:.1f}%"
                    for case in cases
                )

                message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content=f"📋 <b>Список расследований:</b>\n\n{cases_text}\n\n"
                    f"<i>Используйте /case &lt;id&gt; для просмотра деталей</i>",
                    format=MessageFormat.HTML,
                )

            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info(f"Cases list sent to chat {update.effective_chat.id}")

        except Exception as e:
            logger.error(f"Error in list_cases_command: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Произошла ошибка при получении списка расследований",
            )

    async def case_info_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /case"""
        try:
            logger.info(f"Retrieving case info for chat {update.effective_chat.id}")

            # Проверяем инициализацию сервиса
            if not hasattr(self, "case_service") or self.case_service is None:
                logger.error("Case service not initialized")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Внутренняя ошибка: сервис не инициализирован",
                )
                return

            # Получаем ID дела из аргументов команды
            if not context.args:
                logger.warning("No case ID provided")
                error_message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="❌ Укажите ID дела: /case <id>",
                    format=MessageFormat.MARKDOWN,
                )
                await self.telegram_client.send_message(
                    update.effective_chat.id, error_message
                )
                return

            # Проверяем формат ID
            try:
                case_id = UUID(context.args[0])
                logger.debug(f"Parsed case ID: {case_id}")
            except ValueError:
                logger.warning(f"Invalid case ID format: {context.args[0]}")
                error_message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="❌ Неверный формат ID дела. Используйте формат UUID.",
                    format=MessageFormat.MARKDOWN,
                )
                await self.telegram_client.send_message(
                    update.effective_chat.id, error_message
                )
                return

            # Получаем информацию о расследовании
            logger.debug(f"Calling case_service.get_case for ID {case_id}")
            case = await self.case_service.get_case(case_id)

            if not case:
                logger.warning(f"Case with ID {case_id} not found")
                error_message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content=f"❌ Дело #{case_id} не найдено",
                    format=MessageFormat.MARKDOWN,
                )
                await self.telegram_client.send_message(
                    update.effective_chat.id, error_message
                )
                return

            logger.info(f"Retrieved case {case_id}")

            # Формируем сообщение с информацией о деле
            keyboard_buttons = [
                [
                    Button(
                        text="🔍 Исследовать локацию",
                        callback_data=f"explore_{case.id}",
                    ),
                    Button(
                        text="🗺 Карта локаций",
                        callback_data=f"locations_{case.id}",
                    ),
                ],
                [
                    Button(
                        text="🔮 Улики",
                        callback_data=f"evidence_{case.id}",
                    ),
                    Button(
                        text="📝 Анализ",
                        callback_data=f"analyze_{case.id}",
                    ),
                ],
            ]

            message = OutboundMessage(
                recipient_id=str(update.effective_chat.id),
                content=(
                    f"🗂 *Дело #{case.id}*\n\n"
                    f"*Название:* {case.title}\n"
                    f"*Описание:* {case.description}\n"
                    f"*Статус:* {'🟢 Активно' if case.status == 'active' else '🔴 Закрыто'}\n"
                    f"*Прогресс:* {case.progress * 100:.1f}%\n\n"
                    "_Используйте кнопки ниже для взаимодействия с делом_"
                ),
                format=MessageFormat.MARKDOWN,
                keyboard_buttons=keyboard_buttons,
            )
            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info(f"Case info sent to chat {update.effective_chat.id}")

        except ValueError as e:
            logger.error(f"Value error in case_info_command: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id, "❌ Неверный формат ID дела"
            )
        except Exception as e:
            logger.error(f"Error in case_info_command: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Произошла ошибка при получении информации о деле",
            )

    async def button_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        if not query:
            return

        try:
            # Получаем данные из callback_data
            callback_data = query.data
            parts = callback_data.split("_")

            # Должно быть минимум 2 части: действие и id дела
            if len(parts) < 2:
                await self.telegram_client.answer_callback(
                    query.id, text="❌ Неверный формат данных"
                )
                return

            action = parts[0]
            case_id_str = parts[1]

            try:
                # Восстанавливаем полный UUID из первых 8 символов
                case = await self.case_service.get_case(UUID(case_id_str))
                if not case:
                    await self.telegram_client.answer_callback(
                        query.id, text="❌ Дело не найдено"
                    )
                    return
                case_id = case.id
            except ValueError:
                await self.telegram_client.answer_callback(
                    query.id, text="❌ Неверный формат ID дела"
                )
                return

            # Обрабатываем различные действия
            if action == "explore":
                await self._handle_explore(update, case_id)
            elif action == "locations":
                await self._handle_show_locations(update, case_id)
            elif action == "evidence":
                await self._handle_show_evidence(update, case_id)
            elif action == "analyze":
                await self._handle_analyze(update, case_id)
            elif action == "loc":
                # Обработка выбора конкретной локации
                if len(parts) < 3:
                    await self.telegram_client.answer_callback(
                        query.id, text="❌ Неверный формат данных локации"
                    )
                    return
                location_id_str = parts[2]
                try:
                    # Находим локацию по первым 8 символам UUID
                    location = next(
                        (
                            loc
                            for loc in case.locations
                            if str(loc.id)[:8] == location_id_str
                        ),
                        None,
                    )
                    if not location:
                        await self.telegram_client.answer_callback(
                            query.id, text="❌ Локация не найдена"
                        )
                        return
                    await self._handle_location(update, case_id, location.id)
                except ValueError:
                    await self.telegram_client.answer_callback(
                        query.id, text="❌ Неверный формат ID локации"
                    )
            elif action == "case":
                # Обработка возврата к делу
                await self.case_info_command(update, context)
            elif action == "analyze_evidence":
                # Обработка анализа улики
                if len(parts) < 3:
                    await self.telegram_client.answer_callback(
                        query.id, text="❌ Неверный формат данных улики"
                    )
                    return
                evidence_id_str = parts[2]
                try:
                    # Находим улику по первым 8 символам UUID
                    evidence = next(
                        (
                            ev
                            for loc in case.locations
                            for ev in loc.evidence
                            if str(ev.id)[:8] == evidence_id_str
                        ),
                        None,
                    )
                    if not evidence:
                        await self.telegram_client.answer_callback(
                            query.id, text="❌ Улика не найдена"
                        )
                        return
                    await self._handle_analyze_evidence(update, case_id, evidence.id)
                except ValueError:
                    await self.telegram_client.answer_callback(
                        query.id, text="❌ Неверный формат ID улики"
                    )
            else:
                await self.telegram_client.answer_callback(
                    query.id, text="❌ Неизвестное действие"
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {str(e)}", exc_info=True)
            await self.telegram_client.answer_callback(
                query.id, text="❌ Произошла ошибка"
            )

    async def _handle_explore(self, update: Update, case_id: UUID) -> None:
        """Обработка команды исследования локаций"""
        try:
            logger.info(f"Starting location exploration for case {case_id}")

            # Получаем дело
            case = await self.case_service.get_case(case_id)
            if not case:
                logger.error(f"Case {case_id} not found")
                await self.telegram_client.send_message(
                    update.effective_chat.id,
                    OutboundMessage(
                        recipient_id=str(update.effective_chat.id),
                        content="❌ Дело не найдено",
                    ),
                )
                return

            logger.debug(
                f"Found case: {case.title} with {len(case.locations)} locations"
            )

            # Формируем кнопки для каждой локации
            location_buttons = []
            available_locations = [loc for loc in case.locations if loc.is_available]

            for location in available_locations:
                logger.debug(f"Adding button for location: {location.name}")
                row = [
                    Button(
                        text=f"📍 {location.name}",
                        callback_data=f"loc_{str(case_id)[:8]}_{str(location.id)[:8]}",
                    )
                ]
                location_buttons.append(row)

            # Добавляем кнопку возврата
            location_buttons.append(
                [
                    Button(
                        text="🔙 Вернуться к делу",
                        callback_data=f"case_{str(case_id)[:8]}",
                    )
                ]
            )

            logger.debug(f"Created {len(location_buttons)} button rows")

            message = OutboundMessage(
                recipient_id=str(update.effective_chat.id),
                content=(
                    f"🗺 *Доступные локации*\n\n"
                    f"Выберите локацию для исследования:\n"
                    f"Всего локаций: {len(case.locations)}\n"
                    f"Доступно: {len(available_locations)}"
                ),
                format=MessageFormat.MARKDOWN,
                keyboard_buttons=location_buttons,
            )

            logger.info(f"Sending location list to chat {update.effective_chat.id}")
            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info("Location list sent successfully")

        except Exception as e:
            logger.error(f"Error in _handle_explore: {str(e)}", exc_info=True)
            error_message = OutboundMessage(
                recipient_id=str(update.effective_chat.id),
                content="❌ Произошла ошибка при показе локаций. Пожалуйста, попробуйте позже.",
            )
            await self.telegram_client.send_message(
                update.effective_chat.id, error_message
            )

    async def _handle_show_locations(self, update: Update, case_id: UUID) -> None:
        """Обработка показа карты локаций"""
        case = await self.case_service.get_case(case_id)
        if not case:
            await self.telegram_client.send_message(
                update.effective_chat.id,
                OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="❌ Дело не найдено",
                ),
            )
            return

        # Формируем описание локаций
        locations_text = "\n\n".join(
            f"🔍 *{loc.name}*\n"
            f"_{loc.description}_\n"
            f"Уровень риска: {'🔴' if loc.risk_level > 7 else '🟡' if loc.risk_level > 3 else '🟢'}"
            for loc in case.locations
        )

        message = OutboundMessage(
            recipient_id=str(update.effective_chat.id),
            content=f"🗺 *Карта локаций:*\n\n{locations_text}",
            format=MessageFormat.MARKDOWN,
        )
        await self.telegram_client.send_message(update.effective_chat.id, message)

    async def _handle_show_evidence(self, update: Update, case_id: UUID) -> None:
        """Обработка показа списка улик"""
        try:
            logger.info(f"Showing evidence for case {case_id}")

            case = await self.case_service.get_case(case_id)
            if not case:
                logger.error(f"Case {case_id} not found")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Дело не найдено",
                )
                return

            # Собираем все улики из локаций
            evidence_list = []
            evidence_buttons = []

            for location in case.locations:
                for evidence in location.evidence:
                    evidence_list.append(
                        f"🔍 *{evidence.name}*\n"
                        f"_{evidence.description}_\n"
                        f"Найдено в: {location.name}"
                    )

                    # Добавляем кнопку для анализа улики
                    row = [
                        Button(
                            text=f"🔍 {evidence.name}",
                            callback_data=f"analyze_evidence_{str(case_id)[:8]}_{str(evidence.id)[:8]}",
                        )
                    ]
                    evidence_buttons.append(row)

            # Добавляем кнопки навигации
            navigation_buttons = [
                [
                    Button(
                        text="🔙 Вернуться к делу",
                        callback_data=f"case_{str(case_id)[:8]}",
                    )
                ]
            ]
            evidence_buttons.extend(navigation_buttons)

            if not evidence_list:
                message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="🔍 *Список улик пуст*\n\n_Исследуйте локации, чтобы найти улики_",
                    format=MessageFormat.MARKDOWN,
                    keyboard_buttons=navigation_buttons,
                )
            else:
                evidence_text = "\n\n".join(evidence_list)
                message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content=f"🔍 *Найденные улики:*\n\n{evidence_text}",
                    format=MessageFormat.MARKDOWN,
                    keyboard_buttons=evidence_buttons,
                )

            logger.info(f"Sending evidence list to chat {update.effective_chat.id}")
            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info("Evidence list sent successfully")

        except Exception as e:
            logger.error(f"Error in _handle_show_evidence: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Произошла ошибка при показе улик. Пожалуйста, попробуйте позже.",
            )

    async def _handle_analyze(self, update: Update, case_id: UUID) -> None:
        """Обработка анализа улик"""
        try:
            logger.info(f"Starting evidence analysis for case {case_id}")

            case = await self.case_service.get_case(case_id)
            if not case:
                logger.error(f"Case {case_id} not found")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Дело не найдено",
                )
                return

            # Собираем все найденные улики для анализа
            evidence_buttons = []
            for location in case.locations:
                for evidence in location.evidence:
                    if evidence.is_discovered:
                        row = [
                            Button(
                                text=f"🔍 {evidence.name}",
                                callback_data=f"analyze_evidence_{str(case_id)[:8]}_{str(evidence.id)[:8]}",
                            )
                        ]
                        evidence_buttons.append(row)

            # Добавляем кнопки навигации
            navigation_buttons = [
                [
                    Button(
                        text="🔙 Вернуться к делу",
                        callback_data=f"case_{str(case_id)[:8]}",
                    )
                ]
            ]
            evidence_buttons.extend(navigation_buttons)

            if not evidence_buttons:
                message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="🔍 *Нет улик для анализа*\n\n_Исследуйте локации, чтобы найти улики_",
                    format=MessageFormat.MARKDOWN,
                    keyboard_buttons=navigation_buttons,
                )
            else:
                message = OutboundMessage(
                    recipient_id=str(update.effective_chat.id),
                    content="🔍 *Выберите улику для анализа:*",
                    format=MessageFormat.MARKDOWN,
                    keyboard_buttons=evidence_buttons,
                )

            logger.info(f"Sending analysis options to chat {update.effective_chat.id}")
            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info("Analysis options sent successfully")

        except Exception as e:
            logger.error(f"Error in _handle_analyze: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Произошла ошибка при анализе улик. Пожалуйста, попробуйте позже.",
            )

    async def _handle_location(
        self, update: Update, case_id: UUID, location_id: UUID
    ) -> None:
        """Обработка исследования конкретной локации"""
        try:
            logger.info(
                f"Starting location exploration for case {case_id}, location {location_id}"
            )

            # Получаем дело
            case = await self.case_service.get_case(case_id)
            if not case:
                logger.error(f"Case {case_id} not found")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Дело не найдено",
                )
                return

            # Находим локацию
            location = next(
                (loc for loc in case.locations if loc.id == location_id), None
            )
            if not location:
                logger.error(f"Location {location_id} not found in case {case_id}")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Локация не найдена",
                )
                return

            logger.debug(f"Found location: {location.name}")

            # Получаем описание локации
            try:
                description = await self.case_service.generate_location_description(
                    case, location, case.discovered_evidence
                )
                logger.debug("Generated location description")
            except Exception as e:
                logger.error(f"Error generating location description: {e}")
                description = location.description

            # Формируем кнопки для улик
            evidence_buttons = []
            undiscovered_evidence = [
                ev for ev in location.evidence if not ev.is_discovered
            ]

            for evidence in undiscovered_evidence:
                logger.debug(f"Adding button for evidence: {evidence.name}")
                row = [
                    Button(
                        text=f"🔍 {evidence.name}",
                        callback_data=f"analyze_evidence_{str(case_id)[:8]}_{str(evidence.id)[:8]}",
                    )
                ]
                evidence_buttons.append(row)

            # Добавляем кнопки навигации
            navigation_buttons = [
                [
                    Button(
                        text="🔙 Вернуться к списку локаций",
                        callback_data=f"explore_{str(case_id)[:8]}",
                    )
                ],
                [
                    Button(
                        text="🔙 Вернуться к делу",
                        callback_data=f"case_{str(case_id)[:8]}",
                    )
                ],
            ]
            evidence_buttons.extend(navigation_buttons)

            logger.debug(f"Created {len(evidence_buttons)} button rows")

            # Формируем сообщение
            message = OutboundMessage(
                recipient_id=str(update.effective_chat.id),
                content=(
                    f"📍 *{location.name}*\n\n"
                    f"{description}\n\n"
                    f"*Уровень риска:* {'⚠️' * location.risk_level}\n"
                    f"*Найдено улик:* {len([ev for ev in location.evidence if ev.is_discovered])}\n"
                    f"*Доступно для исследования:* {len(undiscovered_evidence)}"
                ),
                format=MessageFormat.MARKDOWN,
                keyboard_buttons=evidence_buttons,
            )

            logger.info(f"Sending location details to chat {update.effective_chat.id}")
            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info("Location details sent successfully")

        except Exception as e:
            logger.error(f"Error in _handle_location: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Произошла ошибка при исследовании локации. Пожалуйста, попробуйте позже.",
            )

    async def _handle_analyze_evidence(
        self, update: Update, case_id: UUID, evidence_id: UUID
    ) -> None:
        """Обработка анализа конкретной улики"""
        try:
            logger.info(
                f"Starting evidence analysis for case {case_id}, evidence {evidence_id}"
            )

            case = await self.case_service.get_case(case_id)
            if not case:
                logger.error(f"Case {case_id} not found")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Дело не найдено",
                )
                return

            # Находим улику
            evidence = next(
                (
                    ev
                    for loc in case.locations
                    for ev in loc.evidence
                    if ev.id == evidence_id
                ),
                None,
            )
            if not evidence:
                logger.error(f"Evidence {evidence_id} not found in case {case_id}")
                await self._send_error_message(
                    update.effective_chat.id,
                    "❌ Улика не найдена",
                )
                return

            logger.debug(f"Found evidence: {evidence.name}")

            # Получаем описание улики
            try:
                description = await self.case_service.generate_evidence_description(
                    case, evidence, case.discovered_evidence
                )
                logger.debug("Generated evidence description")
            except Exception as e:
                logger.error(f"Error generating evidence description: {e}")
                description = evidence.description

            # Формируем сообщение с информацией о улике
            message = OutboundMessage(
                recipient_id=str(update.effective_chat.id),
                content=(
                    f"🔍 *Улика #{evidence.id}*\n\n"
                    f"*Название:* {evidence.name}\n"
                    f"*Описание:* {description}\n"
                    f"*Найдено в:* {evidence.location.name}\n"
                    f"*Статус:* {'🟢 Активно' if evidence.is_discovered else '🔴 Закрыто'}"
                ),
                format=MessageFormat.MARKDOWN,
            )
            await self.telegram_client.send_message(update.effective_chat.id, message)
            logger.info(f"Evidence info sent to chat {update.effective_chat.id}")

        except Exception as e:
            logger.error(f"Error in _handle_analyze_evidence: {str(e)}", exc_info=True)
            await self._send_error_message(
                update.effective_chat.id,
                "❌ Произошла ошибка при получении информации о улике",
            )

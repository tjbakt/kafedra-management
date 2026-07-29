class AcademicYearClosingError(Exception):
    """
    Ошибка закрытия или повторного открытия
    учебного года.
    """

    def __init__(
        self,
        message,
        *,
        code="academic_year_closing_error",
        details=None,
    ):
        super().__init__(message)

        self.message = message
        self.code = code
        self.details = details or {}
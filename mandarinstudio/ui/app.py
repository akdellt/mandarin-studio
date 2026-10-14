
import logging
import threading
from pathlib import Path

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from mandarinstudio.audio.recording import record_audio
from mandarinstudio.comparison.dtw import DtwResult, run_dtw
from mandarinstudio.comparison.evaluation import (
    CategoryOptions,
    evaluate_pronunciation,
)
from mandarinstudio.config import AUDIO_USER_DIR
from mandarinstudio.flashcards.creation import create_flashcard
from mandarinstudio.flashcards.models import Flashcard
from mandarinstudio.flashcards.storage import (
    delete_flashcard,
    load_all_flashcards,
    save_flashcard,
)
from mandarinstudio.visualization.graphs import plot_graph

logger = logging.getLogger(__name__)

BACKGROUND_COLOR = "#211A2B"
SURFACE_COLOR = "#2D2340"
ACCENT_COLOR = "#9B7EDE"
ACCENT_HOVER_COLOR = "#B095F0"
TEXT_COLOR = "#FFF8E7"
MUTED_TEXT_COLOR = "#D8CFE8"


class MandarinStudioApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Mandarin Studio")
        self.geometry("960x720")
        self.minsize(720, 560)
        self.configure(fg_color=BACKGROUND_COLOR)

        self._flashcards: list[Flashcard] = []
        self._selected_flashcard: Flashcard | None = None
        self._editing_flashcard: Flashcard | None = None
        self._practice_index = 0
        self._recording_thread: threading.Thread | None = None
        self._graph_canvas: FigureCanvasTkAgg | None = None

        self._build_navigation()
        self._build_creation_view()
        self._build_practice_view()
        self._build_flashcards_view()
        self._load_flashcards()
        if self._flashcards:
            self._show_practice_view()
        else:
            self._show_creation_view()

    def _build_navigation(self) -> None:
        navigation = ctk.CTkFrame(self, fg_color="transparent")
        navigation.pack(fill="x", padx=12, pady=(12, 0))
        navigation_buttons = ctk.CTkFrame(navigation, fg_color="transparent")
        navigation_buttons.pack(anchor="center")
        ctk.CTkButton(
            navigation_buttons,
            text="Criar flashcard",
            command=self._start_new_flashcard,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER_COLOR,
            text_color=TEXT_COLOR,
        ).pack(side="left", padx=6, pady=6)
        self._practice_nav_button = ctk.CTkButton(
            navigation_buttons,
            text="Praticar",
            command=self._show_practice_view,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER_COLOR,
            text_color=TEXT_COLOR,
        )
        self._practice_nav_button.pack(side="left", padx=6, pady=6)
        self._flashcards_nav_button = ctk.CTkButton(
            navigation_buttons,
            text="Flashcards",
            command=self._show_flashcards_view,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER_COLOR,
            text_color=TEXT_COLOR,
        )
        self._flashcards_nav_button.pack(side="left", padx=6, pady=6)

    def _build_creation_view(self) -> None:
        self._creation_view = ctk.CTkFrame(self, fg_color=SURFACE_COLOR)
        self._creation_form = ctk.CTkFrame(
            self._creation_view,
            width=560,
            height=390,
            fg_color="transparent",
        )
        self._creation_form.pack(anchor="center", pady=40)
        self._creation_form.pack_propagate(False)
        ctk.CTkLabel(
            self._creation_form,
            text="Criar flashcard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(padx=20, pady=(20, 12))
        self._creation_title = self._creation_form.winfo_children()[-1]
        self._hanzi_entry = ctk.CTkEntry(
            self._creation_form,
            placeholder_text="Caractere",
            fg_color=SURFACE_COLOR,
            border_color=ACCENT_COLOR,
            text_color=TEXT_COLOR,
            placeholder_text_color=MUTED_TEXT_COLOR,
            height=54,
            font=ctk.CTkFont(size=18),
        )
        self._hanzi_entry.pack(fill="x", padx=42, pady=8)
        self._meaning_entry = ctk.CTkEntry(
            self._creation_form,
            placeholder_text="Tradução",
            fg_color=SURFACE_COLOR,
            border_color=ACCENT_COLOR,
            text_color=TEXT_COLOR,
            placeholder_text_color=MUTED_TEXT_COLOR,
            height=54,
            font=ctk.CTkFont(size=18),
        )
        self._meaning_entry.pack(fill="x", padx=42, pady=8)
        self._creation_status = ctk.CTkLabel(
            self._creation_form,
            text="",
            text_color=MUTED_TEXT_COLOR,
        )
        self._creation_status.pack(padx=20, pady=8)
        self._save_flashcard_button = ctk.CTkButton(
            self._creation_form,
            text="Criar",
            command=self._create_flashcard,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER_COLOR,
            text_color=TEXT_COLOR,
            height=48,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self._save_flashcard_button.pack(padx=42, pady=(8, 20), fill="x")

    def _build_practice_view(self) -> None:
        self._practice_view = ctk.CTkFrame(self, fg_color="transparent")
        self._practice_intro = ctk.CTkFrame(
            self._practice_view,
            fg_color=SURFACE_COLOR,
        )
        ctk.CTkLabel(
            self._practice_intro,
            text="Prática de flashcards",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(padx=20, pady=(20, 12))
        ctk.CTkButton(
            self._practice_intro,
            text="Iniciar prática",
            command=self._start_practice,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER_COLOR,
            text_color=TEXT_COLOR,
        ).pack(padx=20, pady=20)
        self._practice_intro.pack(fill="both", expand=True)

        self._practice_card = ctk.CTkFrame(self._practice_view, fg_color="transparent")
        self._card_label = ctk.CTkLabel(
            self._practice_card,
            text="",
            font=ctk.CTkFont(size=56, weight="bold"),
            text_color=TEXT_COLOR,
        )
        self._card_label.pack(padx=20, pady=6)
        self._record_button = ctk.CTkButton(
            self._practice_card,
            text="Gravar",
            command=self._start_recording,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER_COLOR,
            text_color=TEXT_COLOR,
        )
        self._record_button.pack(padx=20, pady=8)
        self._practice_status = ctk.CTkLabel(
            self._practice_card,
            text="",
            text_color=MUTED_TEXT_COLOR,
        )
        self._practice_status.pack(padx=20, pady=6)
        self._result_label = ctk.CTkLabel(
            self._practice_card,
            text="",
            text_color=TEXT_COLOR,
        )
        self._result_label.pack(padx=20, pady=6)
        self._graph_frame = ctk.CTkFrame(
            self._practice_card,
            fg_color=SURFACE_COLOR,
        )
        self._graph_frame.pack(fill="both", expand=True, padx=20, pady=(6, 12))
        self._next_button = ctk.CTkButton(
            self._practice_card,
            text="Próximo",
            command=self._show_next_flashcard,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER_COLOR,
            text_color=TEXT_COLOR,
        )
        self._next_button.pack_forget()

    def _build_flashcards_view(self) -> None:
        self._flashcards_view = ctk.CTkFrame(self, fg_color=SURFACE_COLOR)
        ctk.CTkLabel(
            self._flashcards_view,
            text="Flashcards cadastrados",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(padx=20, pady=(20, 12))
        self._flashcards_list = ctk.CTkScrollableFrame(
            self._flashcards_view,
            fg_color="transparent",
        )
        self._flashcards_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _show_creation_view(self) -> None:
        self._practice_view.pack_forget()
        self._flashcards_view.pack_forget()
        self._creation_view.pack(fill="both", expand=True, padx=12, pady=12)

    def _start_new_flashcard(self) -> None:
        self._editing_flashcard = None
        self._hanzi_entry.delete(0, "end")
        self._meaning_entry.delete(0, "end")
        self._creation_status.configure(text="")
        self._creation_title.configure(text="Criar flashcard")
        self._save_flashcard_button.configure(text="Criar")
        self._show_creation_view()

    def _show_practice_view(self) -> None:
        self._creation_view.pack_forget()
        self._flashcards_view.pack_forget()
        if not self._flashcards:
            self._practice_view.pack_forget()
            self._show_creation_view()
            return
        self._practice_view.pack(fill="both", expand=True, padx=12, pady=12)
        self._reset_practice_view()

    def _show_flashcards_view(self) -> None:
        if not self._flashcards:
            self._show_creation_view()
            return
        self._creation_view.pack_forget()
        self._practice_view.pack_forget()
        self._flashcards_view.pack(fill="both", expand=True, padx=12, pady=12)
        self._refresh_flashcards_view()

    def _load_flashcards(self) -> None:
        self._flashcards = load_all_flashcards()
        if (
            self._selected_flashcard is not None
            and all(
                card.id != self._selected_flashcard.id
                for card in self._flashcards
            )
        ):
            self._reset_practice_view()
        if self._flashcards:
            self._practice_nav_button.pack(side="left", padx=6, pady=6)
            self._flashcards_nav_button.pack(side="left", padx=6, pady=6)
        else:
            self._practice_nav_button.pack_forget()
            self._flashcards_nav_button.pack_forget()
            self._flashcards_view.pack_forget()

    def _create_flashcard(self) -> None:
        hanzi = self._hanzi_entry.get().strip()
        meaning = self._meaning_entry.get().strip()
        if not hanzi or not meaning:
            self._creation_status.configure(text="Preencha hanzi e meaning.")
            return

        try:
            flashcard = create_flashcard(hanzi, meaning)
            save_flashcard(flashcard)
            if self._editing_flashcard is not None:
                delete_flashcard(self._editing_flashcard.id)
        except (OSError, RuntimeError, ValueError) as error:
            logger.exception("Unable to create flashcard.")
            self._creation_status.configure(text=f"Erro: {error}")
            return

        self._hanzi_entry.delete(0, "end")
        self._meaning_entry.delete(0, "end")
        self._creation_status.configure(
            text=f"Flashcard criado: {flashcard.hanzi} ({flashcard.pinyin})",
        )
        self._editing_flashcard = None
        self._creation_title.configure(text="Criar flashcard")
        self._save_flashcard_button.configure(text="Criar")
        self._load_flashcards()
        self._show_practice_view()

    def _refresh_flashcards_view(self) -> None:
        for child in self._flashcards_list.winfo_children():
            child.destroy()

        for flashcard in self._flashcards:
            row = ctk.CTkFrame(self._flashcards_list, fg_color=BACKGROUND_COLOR)
            row.pack(fill="x", padx=6, pady=6)
            ctk.CTkLabel(
                row,
                text=f"{flashcard.hanzi}  |  {flashcard.pinyin}  |  {flashcard.meaning}",
                text_color=TEXT_COLOR,
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=12, pady=12)
            ctk.CTkButton(
                row,
                text="Praticar",
                width=100,
                command=lambda card=flashcard: self._practice_specific_card(card),
                fg_color=ACCENT_COLOR,
                hover_color=ACCENT_HOVER_COLOR,
                text_color=TEXT_COLOR,
            ).pack(side="right", padx=4, pady=8)
            ctk.CTkButton(
                row,
                text="Editar",
                width=80,
                command=lambda card=flashcard: self._edit_flashcard(card),
                fg_color=ACCENT_COLOR,
                hover_color=ACCENT_HOVER_COLOR,
                text_color=TEXT_COLOR,
            ).pack(side="right", padx=4, pady=8)
            ctk.CTkButton(
                row,
                text="Deletar",
                width=80,
                command=lambda card=flashcard: self._delete_flashcard(card),
                fg_color="#8E536B",
                hover_color="#B86B88",
                text_color=TEXT_COLOR,
            ).pack(side="right", padx=4, pady=8)

    def _practice_specific_card(self, flashcard: Flashcard) -> None:
        self._practice_index = self._flashcards.index(flashcard)
        self._show_practice_view()
        self._practice_intro.pack_forget()
        self._practice_card.pack(fill="both", expand=True)
        self._display_current_flashcard()

    def _edit_flashcard(self, flashcard: Flashcard) -> None:
        self._editing_flashcard = flashcard
        self._hanzi_entry.delete(0, "end")
        self._hanzi_entry.insert(0, flashcard.hanzi)
        self._meaning_entry.delete(0, "end")
        self._meaning_entry.insert(0, flashcard.meaning)
        self._creation_title.configure(text="Editar flashcard")
        self._save_flashcard_button.configure(text="Salvar alterações")
        self._creation_status.configure(text="")
        self._show_creation_view()

    def _delete_flashcard(self, flashcard: Flashcard) -> None:
        try:
            deleted = delete_flashcard(flashcard.id)
        except (OSError, ValueError) as error:
            logger.exception("Unable to delete flashcard.")
            self._refresh_flashcards_view()
            return

        if deleted:
            self._load_flashcards()
            if self._flashcards:
                self._show_flashcards_view()
            else:
                self._show_creation_view()

    def _start_practice(self) -> None:
        if not self._flashcards:
            self._show_creation_view()
            return

        self._practice_index = 0
        self._practice_intro.pack_forget()
        self._practice_card.pack(fill="both", expand=True)
        self._display_current_flashcard()

    def _reset_practice_view(self) -> None:
        self._selected_flashcard = None
        self._practice_intro.pack(fill="both", expand=True)
        self._practice_card.pack_forget()
        self._next_button.pack_forget()
        self._record_button.configure(state="disabled")
        self._card_label.configure(text="")
        self._practice_status.configure(text="")
        self._result_label.configure(text="")
        self._graph_frame.pack(fill="both", expand=True, padx=20, pady=(6, 12))
        if self._graph_canvas is not None:
            self._graph_canvas.get_tk_widget().destroy()
            self._graph_canvas = None

    def _display_current_flashcard(self) -> None:
        self._selected_flashcard = self._flashcards[self._practice_index]
        self._card_label.configure(text=self._selected_flashcard.hanzi)
        self._record_button.configure(state="normal")
        self._practice_status.configure(text="")
        self._result_label.configure(text="")
        self._next_button.pack_forget()
        self._graph_frame.pack(fill="both", expand=True, padx=20, pady=(6, 12))
        if self._graph_canvas is not None:
            self._graph_canvas.get_tk_widget().destroy()
            self._graph_canvas = None

    def _show_next_flashcard(self) -> None:
        self._practice_index = (self._practice_index + 1) % len(self._flashcards)
        self._display_current_flashcard()

    def _start_recording(self) -> None:
        if self._selected_flashcard is None:
            return
        if self._recording_thread is not None and self._recording_thread.is_alive():
            return

        flashcard = self._selected_flashcard
        recording_path = AUDIO_USER_DIR / f"{flashcard.id}.wav"
        self._record_button.configure(state="disabled")
        self._practice_status.configure(text="Gravando...")
        self._recording_thread = threading.Thread(
            target=self._record_and_evaluate,
            args=(flashcard, recording_path),
            daemon=True,
        )
        self._recording_thread.start()

    def _record_and_evaluate(
        self,
        flashcard: Flashcard,
        recording_path: Path,
    ) -> None:
        try:
            user_audio = record_audio(audio_path=recording_path)
            category, similarity = evaluate_pronunciation(flashcard, user_audio)
            dtw_result = None
            if category != CategoryOptions.INCORRECT or similarity > 0:
                dtw_result = run_dtw(flashcard.reference_audio_path, user_audio)
        except (FileNotFoundError, OSError, RuntimeError, ValueError) as error:
            logger.exception("Unable to evaluate pronunciation.")
            self.after(0, self._show_practice_error, str(error))
            return

        self.after(
            0,
            self._show_practice_result,
            category,
            similarity,
            dtw_result,
            flashcard.meaning,
        )

    def _show_practice_error(self, message: str) -> None:
        self._record_button.configure(state="normal")
        self._practice_status.configure(text=f"Erro: {message}")

    def _show_practice_result(
        self,
        category: CategoryOptions,
        similarity: float,
        dtw_result: DtwResult | None,
        meaning: str,
    ) -> None:
        self._record_button.configure(state="normal")
        self._practice_status.configure(text="Gravação concluída.")
        self._result_label.configure(
            text=(
                f"Significado: {meaning}\n"
                f"{category.value.title()} - similaridade: {similarity:.2f}%"
            ),
        )
        self._next_button.pack(padx=20, pady=(0, 20))

        if dtw_result is None:
            self._graph_frame.pack_forget()
            if self._graph_canvas is not None:
                self._graph_canvas.get_tk_widget().destroy()
                self._graph_canvas = None
            return

        self._graph_frame.pack(fill="both", expand=True, padx=20, pady=(6, 12))
        if self._graph_canvas is not None:
            self._graph_canvas.get_tk_widget().destroy()

        figure: Figure = plot_graph(
            dtw_result.ref_pitch,
            dtw_result.user_pitch,
            dtw_result.path,
            dtw_result.avg_distance,
        )
        self._graph_canvas = FigureCanvasTkAgg(figure, master=self._graph_frame)
        self._graph_canvas.draw()
        self._graph_canvas.get_tk_widget().pack(fill="both", expand=True)


def run() -> None:
    app = MandarinStudioApp()
    app.mainloop()

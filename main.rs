use std::{fs::{self, File}, io::{self, Read}, path::Path, fmt::Debug, path::PathBuf, str::FromStr, ffi::OsString, io::Write, num::NonZeroU64};
#[cfg(feature = "debug")]
use std::env;
#[cfg(unix)]
use std::os::unix::ffi::OsStrExt;
#[cfg(windows)]
use std::os::windows::ffi::OsStrExt;

const NOTE_NAME: [char; 7] = ['도', '레', '미', '파', '솔', '라', '시']; // 계이름 리스트
const NOTE_CODE: [i64; 7] = [0, 2, 4, 5, 7, 9, 11]; // 계이름에 대응하는 값
const INST_LIST: [&str; 11] = ["piano", "bells", "square", "saw", "bass", "organ", "synth", "chime", "violin", "harp", "drum"];

#[derive(Debug, Clone)]
enum Action {
    PlayNote { pitch: String, beat: f64, block: i64 },
    ChangeBeatPerMinutes { beat_per_minutes: f64, beat: f64 },
    ChangeInst { inst: usize, beat: f64, block: i64 },
    Print { text: String, beat: f64 },
    DoNothing { beat: f64 },
}

impl Action {
    fn beat(&self) -> f64 {
        match self {
            Action::PlayNote { beat, .. } => *beat,
            Action::ChangeBeatPerMinutes { beat, .. } => *beat,
            Action::ChangeInst { beat, .. } => *beat,
            Action::Print { beat, .. } => *beat,
            Action::DoNothing { beat } => *beat,
        }
    }

    fn set_beat(&mut self, new_beat: f64) {
        match self {
            Action::PlayNote { beat, .. } => *beat = new_beat,
            Action::ChangeBeatPerMinutes { beat, .. } => *beat = new_beat,
            Action::ChangeInst { beat, .. } => *beat = new_beat,
            Action::Print { beat, .. } => *beat = new_beat,
            Action::DoNothing { beat } => *beat = new_beat,
        }
    }
}

fn main() {
    #[cfg(feature = "debug")]
    println!("디버그 모드 켜짐!");
    // 제목 출력
    println!("{}\n|{:^25}|\n|{:^25}|\n|{:^25}|\n|{:^25}|\n|{:^25}|\n{}", "-".repeat(27), "Sheet2Logic", "version 3.5", "made by jongs", "porting by say_annyeong", "porting to Rust", "-".repeat(27));
    // 사용할 폴더 묻기
    println!("변환할 텍스트 파일이 들어 있는 폴더의 경로를 입력하세요.\n경로 없이 폴더의 이름만 입력하면 현재 프로그램이 위치한 폴더에서 탐색합니다.\n대소문자 관계없이 입력 가능하고, 경로에는 /와 \\ 모두 사용 가능합니다.");
    #[cfg(feature = "debug")]
    println!("\n현재 작업 디렉토리: {:?}", env::current_dir());
    let mut input = String::new();

    // 제대로 된 입력이 들어올 때까지 반복
    let (song_name, text_files_path) = loop {
        println!("{}", "-".repeat(80));

        input.clear();
        match io::stdin().read_line(&mut input) {
            Ok(_) => (),
            Err(error) => {
                println!("{}", error);
                println!("다시 입력해 주세요.");
                continue;
            }
        }

        let folder_path: &Path = Path::new(input.trim()); // 파일 경로로 변경

        #[cfg(feature = "debug")]
        println!("해당 경로: {:?}", folder_path.canonicalize());

        match folder_path.canonicalize() {
            Ok(_) => (),
            Err(error) => {
                println!("{}", error);
                println!("다시 입력해 주세요.");
                continue;
            }
        }

        // 폴더인지 확인
        if !folder_path.is_dir() {
            println!("해당 경로의 폴더를 찾을 수 없습니다.");
            println!("다시 입력해 주세요.");
            continue;
        }

        //let mut midi_files_path = Vec::new();
        let mut text_files_path = Vec::new();

        // 폴더 내 txt파일 개수 세기 및 위치 탐색
        for entry in match fs::read_dir(folder_path) {
            Ok(read_dir) => read_dir,
            Err(error) => {
                println!("{}", error);
                println!("건너뜁니다.");
                continue;
            },
        } {
            let entry = match entry {
                Ok(entry) => entry,
                Err(error) => {
                    println!("{}", error);
                    println!("건너뜁니다.");
                    continue
                },
            };
            let path = entry.path();
            if path.is_file() {
                if path.extension() == Some(std::ffi::OsStr::new("txt")) {
                    text_files_path.push(path);
                } /*else if path.extension() == Some(std::ffi::OsStr::new("mid")) || path.extension() == Some(std::ffi::OsStr::new("midi")) {
                    midi_files_path.push(path);
                }*/
            }
        }

        // 폴더 내 txt 파일이 없음
        if text_files_path.is_empty() {
            println!("해당 경로에 txt 파일이 존재하지 않습니다. 다시 입력해 주세요.");
            println!("건너뜁니다.");
            continue;
        }

        // 폴더 이름을 곡의 제목으로 설정(제한 없음)
        let Some(song_name) = folder_path.file_name().and_then(|name| name.to_str()) else {
            println!("파일 이름을 읽을 수 없음");
            println!("건너뜁니다.");
            continue;
        };

        let song_name = song_name.chars().take(32).collect::<String>();
        text_files_path.sort();

        break (song_name, text_files_path)
    };

    let mut block_num = 0; // 블록 번호(midi track)
    let mut prev_name = String::new(); // 직전에 인식할 파일 이름
    let mut total_sheet: Vec<_> = Vec::new(); // 변환에 필요한 리스트 통합본

    // txt 파일 하나씩 확인
    for file_path in text_files_path {
        let mut file = match File::open(&file_path) {
            Ok(file) => file,
            Err(error) => {
                println!("파일을 열 수 없음! 경로: {}", file_path.display());
                println!("{}", error);
                println!("건너뜁니다.");
                continue;
            }
        };
        let mut sheet = String::new();
        // UTF-8로 읽기 시도
        match file.read_to_string(&mut sheet) {
            Ok(_) => (),
            Err(error) => {
                println!("{} 파일 읽기 실패: {}", file_path.display(), error);
                println!("건너뜁니다.");
                continue;
            }
        }

        if sheet.is_empty() {
            println!("폴더 내 {} 파일은 비어 있습니다.", file_path.display());
            println!("건너뜁니다.");
            continue;
        }

        // .txt제거
        let file_name = match file_path.file_name().and_then(|name| name.to_str().map(|name| match name.rfind('.') {
            Some(index) => &name[..index],
            None => name,
        })) {
            Some(name) => name,
            None => {
                println!("파일 이름 읽기 실패!");
                println!("건너뜁니다.");
                continue
            }
        };

        // 마지막 "-" 앞 부분만
        let prev_file_name = match file_name.rfind('-') {
            Some(index) => &file_name[..index],
            None => file_name,
        };

        // 직전에 남긴 이름과 같음
        if prev_file_name != prev_name {
            block_num += 1; // 블록 번호 1 증가
            prev_name = prev_file_name.to_string(); // 이름 저장
        }

        let mut beat = 0.0;
        let mut intro = Vec::new();
        let mut loop_component = Vec::new();
        let mut is_looping = false;
        let mut loop_count = 0;
        let mut pitch_modifier = 0;
        let mut speed_modifier = 1.0;

        for line in sheet.lines() {
            let words: Vec<_> = line.split_whitespace().collect();

            if words.is_empty() { continue }

            let mut first_word_chars = match words.first().map(|words| words.chars()) {
                Some(first_word) => first_word,
                None => {
                    println!("첫 번째의 음을 읽을 수 없음!");
                    println!("건너뜁니다.");
                    continue
                }
            };

            let first_word_first_char = match first_word_chars.next() {
                Some(first_char) => first_char,
                None => {
                    println!("음을 읽을 수 없음!");
                    println!("건너뜁니다.");
                    continue
                }
            };

            if NOTE_NAME.contains(&first_word_first_char) {
                let note_pitch_index = match NOTE_NAME.iter().position(|char| char == &first_word_first_char) {
                    Some(index) => index,
                    None => {
                        println!("note code의 위치를 찾을 수 없음");
                        println!("건너뜁니다.");
                        continue
                    }
                };
                let mut note_pitch = NOTE_CODE[note_pitch_index];

                let mut other = '\0';
                if let Some(char) = first_word_chars.next() {
                    match char {
                        '#' => {
                            note_pitch += 1;

                        },
                        'b' => note_pitch -= 1,
                        char => other = char
                    }
                }
                note_pitch += pitch_modifier;

                let mut note_octave;
                let other_chars = first_word_chars.as_str();
                if other == '\0' {
                    note_octave = other_chars.trim().parse().unwrap_or(4);
                } else {
                    note_octave = format!("{}{}", other, other_chars).trim().parse().unwrap_or(4);
                }

                while note_pitch < 0 || note_pitch > 11 {
                    if note_pitch < 0 {
                        note_pitch += 12;
                        note_octave -= 1;
                    } else if note_pitch > 11 {
                        note_pitch -= 12;
                        note_octave += 1;
                    }
                }

                let pitch= format!("{}.{:0>2}", note_octave - 1, note_pitch);
                let note_in_range = match pitch.parse::<f64>() {
                    Ok(pitch) => (0.0..7.0).contains(&pitch),
                    Err(error) => {
                        println!("노트 범위를 알 수 없음!");
                        println!("{}", error);
                        true
                    }
                };

                if note_in_range {
                    let action = Action::PlayNote { pitch, beat, block: block_num };
                    if is_looping {
                        loop_component.push(action);
                    } else {
                        intro.push(action);
                    }
                }

                if words.len() > 1 {
                    beat += words[1].trim().parse::<f64>().unwrap_or(0.0).max(0.0) / speed_modifier;
                }

            } else if let Ok(beat_per_minutes) = words[0].trim().parse::<f64>() && beat_per_minutes > 0.0 {
                let action = Action::ChangeBeatPerMinutes { beat_per_minutes, beat };
                if is_looping {
                    loop_component.push(action);
                } else {
                    intro.push(action);
                }

                if words.len() > 1 {
                    beat += words[1].trim().parse::<f64>().unwrap_or(0.0).max(0.0) / speed_modifier;
                }
            } else {
                match first_word_first_char {
                    '!' if words.len() > 1 => {
                        let command = words[0].trim_start_matches('!');
                        match command {
                            "반복" => {
                                if let Ok(count) = words[1].trim().parse::<NonZeroU64>() {
                                    is_looping = true;
                                    loop_count = count.get();
                                    loop_component.push(Action::DoNothing { beat });
                                }
                            }
                            "피치" => {
                                if let Ok(pitch) = words[1].trim().parse() {
                                    pitch_modifier = pitch;
                                }
                            }
                            "속도" => {
                                if let Ok(speed) = words[1].trim().parse::<f64>() && speed > 0.0 {
                                    speed_modifier = speed;
                                }
                            }
                            "악기" => {
                                if let Some(inst) = INST_LIST.iter().position(|&inst| inst == words[1]) {
                                    let action = Action::ChangeInst { inst, beat, block: block_num };
                                    if is_looping {
                                        loop_component.push(action);
                                    } else {
                                        intro.push(action);
                                    }
                                }
                            }
                            _ => ()
                        }
                    }
                    '#' => {
                        if words[0].chars().nth(1) == Some('#') {
                            let text = words[0].chars().skip(2).take(32).collect::<String>().trim().to_string();
                            let action = Action::Print { text, beat };
                            if is_looping {
                                loop_component.push(action);
                            } else {
                                intro.push(action);
                            }
                        }
                    }
                    _ => {
                        if words.len() > 1 {
                            beat += words[1].trim().parse::<f64>().unwrap_or(0.0).max(0.0) / speed_modifier;
                        }
                    }
                }
            }
        }
        total_sheet.extend(intro.clone());

        if !loop_component.is_empty() {
            let loop_start_beat = loop_component[0].beat();
            let loop_duration = beat - loop_start_beat;
            for _ in 0..loop_count {
                total_sheet.extend(loop_component.clone());
                for action in loop_component.iter_mut() {
                    action.set_beat(action.beat() + loop_duration);
                }
            }
        }

        let total_sheet_last_beat = total_sheet.last().map(|last| last.beat());
        let loop_component_first_beat = loop_component.first().map(|first| first.beat());

        if let (Some(last_beat), Some(first_beat)) = (total_sheet_last_beat, loop_component_first_beat) {
            if last_beat < first_beat {
                total_sheet.push(Action::DoNothing { beat: loop_component[0].beat() });
            }
        } else if loop_component.is_empty() && !intro.is_empty() && total_sheet_last_beat.unwrap() < beat {
            total_sheet.push(Action::DoNothing { beat });
        }
    }

    total_sheet.sort_by(|a, b| a.beat().total_cmp(&b.beat()));

    println!("폴더 읽기 완료");

    // 0번째 프로세서 내용 생성
    let process_0 = format!("setrate 100
read playing cell1 0
jump 11 notEqual playing 0
sensor start switch1 @enabled
jump 9 notEqual start 1
set t1 @time
write t1 cell1 1
write 1 cell1 0
jump 11 always
print \"{}\\n\"
jump 20 equal playing 0
control enabled switch1 0
read t1 cell1 1
set t2 @time
op sub t t2 t1
op div t t 10
op idiv t t 1
op div t t 100
print t
print \"\\n\"
print \"[#2030D0]Made with\"
print \"[#FFFF00] S2L 3.5\"\
print \"[#AA8000] for [#FFAA00]Rust\"
printflush message1", song_name);

    // 1번째 이후 프로세서 내용 생성
    let mut current_beat_per_minutes = 150.0;
    let mut beat = 0.0;
    let mut process = Vec::new();
    let mut process_one_page = vec!["setrate 100".to_string(), "read playing cell1 0".to_string(), "jump 1 notEqual playing 1".to_string()];

    let total_sheet_len = total_sheet.len();
    for (index, action) in total_sheet.into_iter().enumerate() {
        let current_total_sheet_beat = action.beat();
        if current_total_sheet_beat > beat {
            let waiting_time = 60.0 * (current_total_sheet_beat - beat) / current_beat_per_minutes;
            process_one_page.push(format!("wait {}", waiting_time));
            overflow_process_code_size(index, total_sheet_len, &mut process_one_page, &mut process);
            beat = current_total_sheet_beat;
        }
        match action {
            Action::PlayNote { pitch, block, .. } => {
                process_one_page.push(format!("control config block{} {}", block, pitch));
                overflow_process_code_size(index, total_sheet_len, &mut process_one_page, &mut process);
            },
            Action::ChangeBeatPerMinutes { beat_per_minutes, .. } => current_beat_per_minutes = beat_per_minutes,
            Action::ChangeInst { inst, block, .. } => {
                process_one_page.push(format!("control color block{} {}", block, inst));
                overflow_process_code_size(index, total_sheet_len, &mut process_one_page, &mut process);
            },
            Action::Print { text, .. } => {
                process_one_page.push(format!("print \"{}\"", text));
                overflow_process_code_size(index, total_sheet_len, &mut process_one_page, &mut process);
            },
            _ => ()
        }
    }

    process_one_page.push("write 0 cell1 0".to_string());
    process.push(process_one_page.join("\n"));

    // 각 페이지를 파일로 저장하기
    println!("프로세서 코드가 작성된 텍스트 파일을 저장할 폴더의 이름 또는 경로를 입력하세요.");
    println!("주의: 입력한 폴더 내에 이름이 같은 파일이 이미 존재할 경우, 기존 파일은 삭제됩니다!");

    'save: loop {
        let mut input = String::new();
        match io::stdin().read_line(&mut input) {
            Ok(_) => (),
            Err(_) => {
                println!("잘못 된 입력");
                continue
            }
        }

        let folder = match PathBuf::from_str(input.trim()) {
            Ok(folder) => folder,
            Err(_) => {
                println!("잘못 된 입력");
                continue
            }
        };

        let read_dir = match folder.read_dir() {
            Ok(read_dir) => read_dir,
            Err(_) => {
                println!("해당 경로의 폴더를 찾을 수 없습니다. 다시 입력해 주세요");
                continue
            }
        };

        println!("{:?} 폴더에 저장합니다", folder);
        let mut existing_files = Vec::new();
        for file in read_dir {
            let file = match file {
                Ok(file) => file,
                Err(error) => {
                    println!("{}", error);
                    continue
                }
            };
            existing_files.push(file.file_name());
        }

        let mut using_file_name = Vec::new();
        // page 0.txt 포함 전체 process 생성, process는 page 0.txt가 제외된 상태이니 길이의 +1만큼 반복
        for i in 0..=process.len() {
            using_file_name.push(format!("page {}.txt", i));
        }

        let is_duplicate = find_duplicates(&existing_files, &using_file_name);

        if !is_duplicate.is_empty() {
            loop {
                println!("중복인 파일: {:?}", is_duplicate);
                println!("파일이 덮어씌워집니다. 계속하시겠습니까?  (y/n)");
                let mut input = String::new();
                match io::stdin().read_line(&mut input) {
                    Ok(_) => (),
                    Err(_) => {
                        println!("잘못된 입력");
                        continue
                    }
                }

                match input.trim() {
                    "y" | "yes" | "Y" | "YES" => {
                        break
                    }
                    "n" | "no" | "N" | "NO" => {
                        println!("저장이 취소되었습니다. 폴더 이름을 다시 입력해 주세요.");
                        continue 'save
                    }
                    _ => {
                        println!("잘못된 입력을 하셨습니다. 다시 입력해 주세요");
                        continue
                    }
                }
            }
        }
        let page0_path = folder.join("page 0.txt");
        if create_and_save_file(page0_path, &process_0).is_none() {
            println!("page 0..txt 저장 실패.");
            println!("중단합니다.");
            continue 'save
        }

        for (index, current_process) in process.iter().enumerate() {
            let page_path = folder.join(format!("page {}.txt", index + 1));
            if create_and_save_file(page_path, &current_process).is_none() {
                continue
            }
        }
        break
    }

    println!("성공적으로 저장되었습니다!");
    println!("{}개의 프로세서를 각각 {}개의 노트블록과 메모리에 연결하세요.", process.len() + 1, block_num);
    println!("Enter를 눌러 종료합니다... ");
    let _ = io::stdin().read_line(&mut String::new());
}

fn overflow_process_code_size(index: usize, total_sheet_len: usize, process_one_page: &mut Vec<String>, process: &mut Vec<String>) {
    if process_one_page.len() >= 999 && index + 1 < total_sheet_len {
        process_one_page.push(format!("write {} cell1 0", process.len() + 2));
        process.push(process_one_page.join("\n"));
        *process_one_page = vec!["setrate 100".to_string(), "read playing cell1 0".to_string(), format!("jump 1 notEqual playing {}", process.len() + 1)];
    }
}

fn find_duplicates(existing_files: &[OsString], target_files: &[String]) -> Vec<String> {
    let mut duplicates = Vec::new();

    for target in target_files {
        let is_duplicate = existing_files.iter().any(|existing| {
            #[cfg(unix)]
            {
                // Unix: 바이트 비교
                existing.as_os_str().as_bytes() == target.as_bytes()
            }

            #[cfg(windows)]
            {
                // Windows: UTF-16 비교
                existing.encode_wide().eq(target.encode_utf16())
            }
        });

        if is_duplicate {
            duplicates.push(target.clone());
        }
    }

    duplicates
}

fn create_and_save_file(page_path: PathBuf, current_process: &str) -> Option<()> {
    let mut file = match File::create(page_path) {
        Ok(file) => file,
        Err(error) => {
            println!("파일 생성 실패");
            println!("{}", error);
            println!("건너뜁니다.");
            return None
        }
    };
    match file.write_all(current_process.as_bytes()) {
        Ok(_) => (),
        Err(error) => {
            println!("파일 쓰기 실패");
            println!("{}", error);
            println!("inner: {}", current_process);
        }
    };
    Some(())
}
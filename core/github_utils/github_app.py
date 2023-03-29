import typing

import github
from github import Github, GithubObject
from dotenv import load_dotenv

from core.github_utils.github_api_auth import get_yeager_app_access_token

load_dotenv()


class YeagerGithubApp:
    def __init__(self, repo_id: str, discord_user_name: str) -> None:
        self.discord_user_name = discord_user_name
        self.repo_id = repo_id
        self.g: Github
        self.org: github.Organization.Organization
        self.repo: github.Repository.Repository
        self.last_file_sha: str

    async def build_app(self) -> None:
        access_token = await get_yeager_app_access_token()
        self.g = Github(access_token)
        self.org = self.g.get_organization("yeagerai")
        print("yoyo! Authenticated with GitHub!")

    async def create_new_repo(
        self,
        workflow_name: str,
        workflow_description: str,
        repo_name: str,
        discord_callbacks: typing.Any,
    ) -> None:
        self.repo = self.org.create_repo(repo_name, private=True)
        await discord_callbacks["send_message"](
            f"Created new repo: {self.repo.name} at {self.repo.html_url}"
        )
        await discord_callbacks["edit_channel_orig_embed"](
            orig_message=discord_callbacks["orig_message"],
            title=f"Workflow: {workflow_name} created by {self.discord_user_name}",
            description=workflow_description,
            github_url=self.repo.html_url,
        )

    async def invite_collaborators(self, discord_callbacks: typing.Any) -> None:
        collaborators_names = await discord_callbacks["add_collaborators"]()

        for collaborator_name in collaborators_names:
            if collaborator_name == "":
                continue
            collaborator = self.g.get_user(collaborator_name)
            try:
                self.repo.add_to_collaborators(collaborator, permission="push")
                await discord_callbacks["send_message"](
                    f"Invited {collaborator_name} to the repo with read and write permissions..."
                )
            except Exception:
                await discord_callbacks["send_message"](
                    f"The collaborator {collaborator_name} was not found on GitHub..."
                )
                continue

    async def create_file_commit_n_push(
        self,
        file_path: str,
        commit_message: str,
        file_content: str,
        discord_callbacks: typing.Any,
    ) -> None:
        self.repo.create_file(
            path=file_path, message=commit_message, content=file_content
        )
        await discord_callbacks["send_message"](
            f"Committed and pushed {file_path.split('/')[-1]} to the repo..."
        )

    async def get_file_content(self, file_path: str) -> str:
        return self.repo.get_contents(file_path).decoded_content.decode()

    async def update_file_commit_n_push(
        self,
        file_path: str,
        commit_message: str,
        file_content: str,
        discord_callbacks: typing.Any,
    ) -> None:
        contents = self.repo.get_contents(file_path)
        file_sha = contents.sha
        self.repo.update_file(
            path=file_path,
            message=commit_message,
            content=file_content,
            sha=file_sha,
        )
        await discord_callbacks["send_message"](
            f"Committed and pushed {file_path.split('/')[-1]} to the repo..."
        )

    def update_sha(self) -> None:
        a = self.repo.get_commits()
        print(self.repo.get_commits())
        self.last_file_sha = a[0].sha

    async def full_commit(
        self,
        commit_message: str,
        files: typing.List[typing.Tuple[str, str]],
        discord_callbacks: typing.Any,
    ) -> None:
        """
        Commits multiple files at the same time.
        The `files` argument is a list of tuples, where each tuple contains a file path
        and its content.
        """
        self.update_sha()

        tree = self.repo.get_git_tree(self.last_file_sha)
        blob_objects = []
        for file_path, file_content in files:
            blob = self.repo.create_git_blob(file_content, "utf-8")
            blob_objects.append(
                github.InputGitTreeElement(
                    path=file_path, mode="100644", type="blob", sha=blob.sha
                )
            )

        tree = self.repo.create_git_tree(blob_objects, base_tree=tree)

        parent_commit = self.repo.get_git_commit(self.last_file_sha)
        commit = self.repo.create_git_commit(commit_message, tree, [parent_commit])
        ref = self.repo.get_git_ref("heads/main")
        ref.edit(commit.sha)

        await discord_callbacks["send_message"](
            f"Committed and pushed {len(files)} files to the repo..."
        )

    async def move_files_n_commit(
        self, source_folder: str, destination_folder: str, branch: str
    ) -> None:
        source_contents = self.repo.get_contents(source_folder, ref=branch)

        try:
            self.repo.get_contents(destination_folder, ref=branch)
        except:
            self.repo.create_file(
                destination_folder + "/placeholder",
                "Creating destination folder",
                "",
                branch=branch,
            )

        self.update_sha()

        base_tree = self.repo.get_git_tree(self.last_file_sha)
        base_commit = self.repo.get_git_commit(self.last_file_sha)

        input_tree_elements = []

        # Add the new tree elements for the moved files
        for file in source_contents:
            content = file.decoded_content.decode()
            if destination_folder == "":
                new_path = file.name
            else:
                new_path = destination_folder + "/" + file.name

            new_blob = self.repo.create_git_blob(content, "utf-8")
            input_tree_elements.append(
                github.InputGitTreeElement(
                    path=new_path, mode="100644", type="blob", sha=new_blob.sha
                )
            )

        # Create the new tree with the new file locations, and merge it with the base tree
        new_tree = self.repo.create_git_tree(input_tree_elements, base_tree=base_tree)

        commit_message = f"Move files from {source_folder} to {destination_folder}"
        new_commit = self.repo.create_git_commit(
            commit_message, new_tree, [base_commit]
        )
        # Update the branch reference to point to the new commit
        self.repo.get_git_ref(f"heads/{branch}").edit(new_commit.sha)
